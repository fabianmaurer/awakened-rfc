// game.cpp

#include "CvGameCoreDLL.h"
#include "CvUnitMastery.h"
#include "CvGameCoreUtils.h"
#include "CvGame.h"
#include "CvGameAI.h"
#include "CvMap.h"
#include "CvPlot.h"
#include "CvPlayerAI.h"
#include "CvRandom.h"
#include "CvTeamAI.h"
#include "CvGlobals.h"
#include "CvInitCore.h"
#include "CvMapGenerator.h"
#include "CvArtFileMgr.h"
#include "CvDiploParameters.h"
#include "CvReplayMessage.h"
#include "CyArgsList.h"
#include "CvInfos.h"
#include "CvPopupInfo.h"
#include "FProfiler.h"
#include "CvReplayInfo.h"
#include "CvGameTextMgr.h"
#include <set>
#include "CvEventReporter.h"
#include "CvMessageControl.h"
#include "ObserverPerformance.h"
#include <map>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include "CvSelectionGroup.h"
#include "CvUnit.h"

#if ARFC_ENABLE_REPORTING
// Bind early benchmark seeding to the same private config/token/PID as Python.
// Ordinary and multiplayer initialization never consume this override.
static bool observerPerformanceSeed(unsigned int& seed, std::string& marker)
{
    const char* config = getenv("AWAKENED_RFC_OBSERVER_CONFIG");
    const char* token = getenv("AWAKENED_RFC_OBSERVER_TOKEN");
    if (!config || !token || !*token) return false;
    char value[256];
    GetPrivateProfileStringA("Observer", "Token", "", value, sizeof(value), config);
    if (strcmp(value, token) != 0) return false;
    if (GetPrivateProfileIntA("Observer", "ProcessId", 0, config) != GetCurrentProcessId()) return false;
    GetPrivateProfileStringA("Observer", "Mode", "", value, sizeof(value), config);
    if (strcmp(value, "performance") != 0) return false;
    GetPrivateProfileStringA("Observer", "Seed", "", value, sizeof(value), config);
    if (!*value || value[0] == '-') return false;
    char* end;
    errno = 0;
    unsigned long parsed = strtoul(value, &end, 10);
    if (*end || errno == ERANGE) return false;
    seed = (unsigned int)parsed;
    marker = config;
    std::string::size_type slash = marker.find_last_of("\\/");
    if (slash == std::string::npos) return false;
    marker = marker.substr(0, slash + 1) + "seed-initialized.ini";
    return true;
}

bool g_observerPerformance = false;
namespace {
    struct ObserverTiming {
        int calls;
        double total, own, maximum;
        int bins[5];
        double binSeconds[5];
        double work;
        ObserverTiming() : calls(0), total(0), own(0), maximum(0), work(0) {
            for (int i = 0; i < 5; ++i) { bins[i] = 0; binSeconds[i] = 0; }
        }
    };
    typedef std::map<std::pair<int, std::string>, ObserverTiming> ObserverTimings;
    ObserverTimings observerTimings;
    ObserverPerformanceScope* observerParent = NULL;
    double observerFrequency = 1;
    std::string observerTimingPath;
    std::string observerRuntimePath;
    __int64 observerLastWall = 0;
    double observerLastProcess = 0, observerLastThread = 0;
    int observerLastTurn = 0;
    double observerFileSeconds(const FILETIME& value) {
        ULARGE_INTEGER ticks;
        ticks.LowPart = value.dwLowDateTime;
        ticks.HighPart = value.dwHighDateTime;
        return double(ticks.QuadPart) / 10000000.0;
    }
    bool observerCpuTimes(double& process, double& thread) {
        FILETIME created, exited, kernel, user;
        if (!GetProcessTimes(GetCurrentProcess(), &created, &exited, &kernel, &user)) return false;
        process = observerFileSeconds(kernel) + observerFileSeconds(user);
        if (!GetThreadTimes(GetCurrentThread(), &created, &exited, &kernel, &user)) return false;
        thread = observerFileSeconds(kernel) + observerFileSeconds(user);
        return true;
    }
    void observerRuntimeSample() {
        if (observerRuntimePath.empty()) return;
        LARGE_INTEGER now;
        QueryPerformanceCounter(&now);
        double process, thread;
        if (!observerCpuTimes(process, thread)) return;
        FILE* file = fopen(observerRuntimePath.c_str(), "a");
        if (!file) return;
        int cities = 0, units = 0, players = 0;
        for (int i = 0; i < MAX_PLAYERS; ++i) {
            CvPlayer& player = GET_PLAYER((PlayerTypes)i);
            if (player.isAlive()) ++players;
            cities += player.getNumCities();
            units += player.getNumUnits();
        }
        fprintf(file, "%d,%d,%.9f,%.9f,%.9f,%d,%d,%d\n", observerLastTurn,
            GC.getGameINLINE().getGameTurn(), double(now.QuadPart - observerLastWall) / observerFrequency,
            process - observerLastProcess, thread - observerLastThread, cities, units, players);
        fclose(file);
        observerLastWall = now.QuadPart;
        observerLastProcess = process;
        observerLastThread = thread;
        observerLastTurn = GC.getGameINLINE().getGameTurn();
    }
}
void observerPerformanceStart()
{
    const char* path = getenv("AWAKENED_RFC_PERFORMANCE_OUTPUT");
    if (!path || !*path) return;
    LARGE_INTEGER frequency;
    if (!QueryPerformanceFrequency(&frequency)) return;
    observerFrequency = double(frequency.QuadPart);
    observerTimingPath = path;
    FILE* file = fopen(path, "w");
    if (!file) return;
    fprintf(file, "turn,calculation,calls,inclusive_seconds,exclusive_seconds,max_seconds,lt_100us,lt_1ms,lt_10ms,lt_100ms,ge_100ms,work_units,lt_100us_seconds,lt_1ms_seconds,lt_10ms_seconds,lt_100ms_seconds,ge_100ms_seconds\n");
    fclose(file);
    observerTimings.clear();
    observerRuntimePath = observerTimingPath.substr(0, observerTimingPath.find_last_of("\\/") + 1) + "performance-runtime.csv";
    file = fopen(observerRuntimePath.c_str(), "w");
    if (file) {
        fprintf(file, "start_turn,end_turn,wall_seconds,process_cpu_seconds,main_thread_cpu_seconds,cities,units,alive_players\n");
        fclose(file);
    }
    LARGE_INTEGER now;
    QueryPerformanceCounter(&now);
    observerLastWall = now.QuadPart;
    observerCpuTimes(observerLastProcess, observerLastThread);
    observerLastTurn = GC.getGameINLINE().getGameTurn();
    g_observerPerformance = true;
}
void observerPerformanceFlush()
{
    if (observerTimingPath.empty() || observerTimings.empty()) return;
    observerRuntimeSample();
    FILE* file = fopen(observerTimingPath.c_str(), "a");
    if (!file) return;
    for (ObserverTimings::iterator it = observerTimings.begin(); it != observerTimings.end(); ++it) {
        const ObserverTiming& t = it->second;
        fprintf(file, "%d,%s,%d,%.9f,%.9f,%.9f,%d,%d,%d,%d,%d,%.0f,%.9f,%.9f,%.9f,%.9f,%.9f\n", it->first.first,
            it->first.second.c_str(), t.calls, t.total, t.own, t.maximum,
            t.bins[0], t.bins[1], t.bins[2], t.bins[3], t.bins[4], t.work,
            t.binSeconds[0], t.binSeconds[1], t.binSeconds[2], t.binSeconds[3], t.binSeconds[4]);
    }
    fclose(file);
    observerTimings.clear();
}
void observerPerformanceCount(const char* name, unsigned int work)
{
    if (!g_observerPerformance) return;
    ObserverTiming& t = observerTimings[std::make_pair(GC.getGameINLINE().getGameTurn(), std::string(name))];
    ++t.calls;
    t.work += work;
}
bool observerPerformanceInScope(const char* name)
{
    if (!g_observerPerformance) return false;
    for (ObserverPerformanceScope* scope = observerParent; scope; scope = scope->m_parent)
        if (scope->m_name && strcmp(scope->m_name, name) == 0) return true;
    return false;
}
ObserverPerformanceScope::ObserverPerformanceScope(const char* name)
    : m_name(NULL), m_children(0), m_work(0), m_parent(NULL)
{
    if (!g_observerPerformance) return;
    m_name = name;
    m_turn = GC.getGameINLINE().getGameTurn();
    m_parent = observerParent;
    observerParent = this;
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    m_start = counter.QuadPart;
}
ObserverPerformanceScope::~ObserverPerformanceScope()
{
    if (!m_name) return;
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    double elapsed = double(counter.QuadPart - m_start) / observerFrequency;
    observerParent = m_parent;
    if (m_parent) m_parent->m_children += elapsed;
    ObserverTiming& t = observerTimings[std::make_pair(m_turn, std::string(m_name))];
    ++t.calls;
    t.work += m_work;
    t.total += elapsed;
    t.own += std::max(0.0, elapsed - m_children);
    t.maximum = std::max(t.maximum, elapsed);
    int bin = elapsed < 0.0001 ? 0 : elapsed < 0.001 ? 1 : elapsed < 0.01 ? 2 : elapsed < 0.1 ? 3 : 4;
    ++t.bins[bin];
    t.binSeconds[bin] += elapsed;
    if (!g_observerPerformance) observerPerformanceFlush();
}

#endif
// interface uses
#include "CvDLLInterfaceIFaceBase.h"
#include "CvDLLEngineIFaceBase.h"
#include "CvDLLPythonIFaceBase.h"

#include "CvRhyes.h" //Rhye

// Public Functions...

CvGame::CvGame()
{
	m_aiRankPlayer = new int[MAX_PLAYERS];        // Ordered by rank...
	m_aiPlayerRank = new int[MAX_PLAYERS];        // Ordered by player ID...
	m_aiPlayerScore = new int[MAX_PLAYERS];       // Ordered by player ID...
	m_aiRankTeam = new int[MAX_TEAMS];						// Ordered by rank...
	m_aiTeamRank = new int[MAX_TEAMS];						// Ordered by team ID...
	m_aiTeamScore = new int[MAX_TEAMS];						// Ordered by team ID...

	m_paiUnitCreatedCount = NULL;
	m_paiUnitClassCreatedCount = NULL;
	m_paiBuildingClassCreatedCount = NULL;
	m_paiProjectCreatedCount = NULL;
	m_paiForceCivicCount = NULL;
	m_paiVoteOutcome = NULL;
	m_paiReligionGameTurnFounded = NULL;
	m_paiCorporationGameTurnFounded = NULL;
	m_aiSecretaryGeneralTimer = NULL;
	m_aiVoteTimer = NULL;
	m_aiDiploVote = NULL;

	m_pabSpecialUnitValid = NULL;
	m_pabSpecialBuildingValid = NULL;
	m_abReligionSlotTaken = NULL;

	m_paHolyCity = NULL;
	m_paHeadquarters = NULL;

	m_pReplayInfo = NULL;

	m_aiShrineBuilding = NULL;
	m_aiShrineReligion = NULL;

	reset(NO_HANDICAP, true);
}


CvGame::~CvGame()
{
	uninit();

	SAFE_DELETE_ARRAY(m_aiRankPlayer);
	SAFE_DELETE_ARRAY(m_aiPlayerRank);
	SAFE_DELETE_ARRAY(m_aiPlayerScore);
	SAFE_DELETE_ARRAY(m_aiRankTeam);
	SAFE_DELETE_ARRAY(m_aiTeamRank);
	SAFE_DELETE_ARRAY(m_aiTeamScore);
}


//Rhye - start (jdog)
void CvGame::logMsg(char* format, ... )
{
	static char buf[2048];
	_vsnprintf( buf, 2048-4, format, (char*)(&format+1) );
	gDLL->logMsg("sdkDbg.log", buf);
}
//Rhye - end


void CvGame::init(HandicapTypes eHandicap)
{
	bool bValid;
	int iStartTurn;
	int iEstimateEndTurn;
	int iI;
	//logMsg("game init"); //Rhye
	//--------------------------------
	// Init saved data
	reset(eHandicap);

	//--------------------------------
	// Init containers
	m_deals.init();
	m_voteSelections.init();
	m_votesTriggered.init();

#if ARFC_ENABLE_REPORTING
	unsigned int benchmarkSeed = 0;
	std::string seedMarker;
	bool benchmarkSeeded = false;
	if (GC.getInitCore().getType() == GAME_SP_NEW || GC.getInitCore().getType() == GAME_SP_SCENARIO)
		benchmarkSeeded = observerPerformanceSeed(benchmarkSeed, seedMarker);
	if (benchmarkSeeded)
	{
		GC.getInitCore().setMapRandSeed(benchmarkSeed);
		GC.getInitCore().setSyncRandSeed(benchmarkSeed);
	}
#endif
	m_mapRand.init(GC.getInitCore().getMapRandSeed() % 73637381);
	m_sorenRand.init(GC.getInitCore().getSyncRandSeed() % 52319761);
#if ARFC_ENABLE_REPORTING
	if (benchmarkSeeded)
	{
		FILE* marker = fopen(seedMarker.c_str(), "w");
		if (marker)
		{
			fprintf(marker, "[Seed]\nValue=%u\nProcessId=%lu\nStage=CvGame.init\nMapSeed=%u\nSyncSeed=%u\n",
				benchmarkSeed, GetCurrentProcessId(), benchmarkSeed % 73637381, benchmarkSeed % 52319761);
			fclose(marker);
		}
	}

#endif

	//--------------------------------
	// Init non-saved data

	//--------------------------------
	// Init other game data

	// Turn off all MP options if it's a single player game
	if (GC.getInitCore().getType() == GAME_SP_NEW ||
		GC.getInitCore().getType() == GAME_SP_SCENARIO)
	{
		for (iI = 0; iI < NUM_MPOPTION_TYPES; ++iI)
		{
			setMPOption((MultiplayerOptionTypes)iI, false);
		}
	}

	// If this is a hot seat game, simultaneous turns is always off
	if (isHotSeat() || isPbem())
	{
		setMPOption(MPOPTION_SIMULTANEOUS_TURNS, false);
	}
	// If we didn't set a time in the Pitboss, turn timer off
	if (isPitboss() && getPitbossTurnTime() == 0)
	{
		setMPOption(MPOPTION_TURN_TIMER, false);
	}

	if (isMPOption(MPOPTION_SHUFFLE_TEAMS))
	{
		int aiTeams[MAX_CIV_PLAYERS];

		int iNumPlayers = 0;
		for (int i = 0; i < MAX_CIV_PLAYERS; i++)
		{
			if (GC.getInitCore().getSlotStatus((PlayerTypes)i) == SS_TAKEN)
			{
				aiTeams[iNumPlayers] = GC.getInitCore().getTeam((PlayerTypes)i);
				++iNumPlayers;
			}
		}

		for (int i = 0; i < iNumPlayers; i++)
		{
			int j = (getSorenRand().get(iNumPlayers - i, NULL) + i);

			if (i != j)
			{
				int iTemp = aiTeams[i];
				aiTeams[i] = aiTeams[j];
				aiTeams[j] = iTemp;
			}
		}

		iNumPlayers = 0;
		for (int i = 0; i < MAX_CIV_PLAYERS; i++)
		{
			if (GC.getInitCore().getSlotStatus((PlayerTypes)i) == SS_TAKEN)
			{
				GC.getInitCore().setTeam((PlayerTypes)i, (TeamTypes)aiTeams[iNumPlayers]);
				++iNumPlayers;
			}
		}
	}

	if (isOption(GAMEOPTION_LOCK_MODS))
	{
		if (isGameMultiPlayer())
		{
			setOption(GAMEOPTION_LOCK_MODS, false);
		}
		else
		{
			static const int iPasswordSize = 8;
			char szRandomPassword[iPasswordSize];
			for (int i = 0; i < iPasswordSize-1; i++)
			{
				szRandomPassword[i] = getSorenRandNum(128, NULL);
			}
			szRandomPassword[iPasswordSize-1] = 0;

			GC.getInitCore().setAdminPassword(szRandomPassword);
		}
	}

	if (getGameTurn() == 0)
	{
		iStartTurn = 0;

		for (iI = 0; iI < GC.getGameSpeedInfo(getGameSpeedType()).getNumTurnIncrements(); iI++)
		{
			iStartTurn += GC.getGameSpeedInfo(getGameSpeedType()).getGameTurnInfo(iI).iNumGameTurnsPerIncrement;
		}

		iStartTurn *= GC.getEraInfo(getStartEra()).getStartPercent();
		iStartTurn /= 100;

		setGameTurn(iStartTurn);
	}

	setStartTurn(getGameTurn());

	if (getMaxTurns() == 0)
	{
		iEstimateEndTurn = 0;

		for (iI = 0; iI < GC.getGameSpeedInfo(getGameSpeedType()).getNumTurnIncrements(); iI++)
		{
			iEstimateEndTurn += GC.getGameSpeedInfo(getGameSpeedType()).getGameTurnInfo(iI).iNumGameTurnsPerIncrement;
		}

		setEstimateEndTurn(iEstimateEndTurn);

		if (getEstimateEndTurn() > getGameTurn())
		{
			bValid = false;

			for (iI = 0; iI < GC.getNumVictoryInfos(); iI++)
			{
				if (isVictoryValid((VictoryTypes)iI))
				{
					if (GC.getVictoryInfo((VictoryTypes)iI).isEndScore())
					{
						bValid = true;
						break;
					}
				}
			}

			if (bValid)
			{
				setMaxTurns(getEstimateEndTurn() - getGameTurn());
			}
		}
	}
	else
	{
		setEstimateEndTurn(getGameTurn() + getMaxTurns());
	}

	setStartYear(GC.getDefineINT("START_YEAR"));

	for (iI = 0; iI < GC.getNumSpecialUnitInfos(); iI++)
	{
		if (GC.getSpecialUnitInfo((SpecialUnitTypes)iI).isValid())
		{
			makeSpecialUnitValid((SpecialUnitTypes)iI);
		}
	}

	for (iI = 0; iI < GC.getNumSpecialBuildingInfos(); iI++)
	{
		if (GC.getSpecialBuildingInfo((SpecialBuildingTypes)iI).isValid())
		{
			makeSpecialBuildingValid((SpecialBuildingTypes)iI);
		}
	}

	AI_init();

	doUpdateCacheOnTurn();
}

//
// Set initial items (units, techs, etc...)
//
void CvGame::setInitialItems()
{
	PROFILE_FUNC();
	//logMsg("setInitialItems"); //Rhye
	initFreeState();
	assignStartingPlots();
	normalizeStartingPlots();
	initFreeUnits();

	for (int i = 0; i < MAX_PLAYERS; ++i)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)i);
		if (kPlayer.isAlive())
		{
			kPlayer.AI_updateFoundValues();
		}
	}
}


void CvGame::regenerateMap()
{
	int iI;
	//logMsg("regenerateMap"); //Rhye
	if (GC.getInitCore().getWBMapScript())
	{
		return;
	}

	setFinalInitialized(false);

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		GET_PLAYER((PlayerTypes)iI).killUnits();
	}

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		GET_PLAYER((PlayerTypes)iI).killCities();
	}

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		GET_PLAYER((PlayerTypes)iI).killAllDeals();
	}

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		GET_PLAYER((PlayerTypes)iI).setFoundedFirstCity(false);
		GET_PLAYER((PlayerTypes)iI).setStartingPlot(NULL, false);
	}

	for (iI = 0; iI < MAX_TEAMS; iI++)
	{
		GC.getMapINLINE().setRevealedPlots(((TeamTypes)iI), false);
	}

	gDLL->getEngineIFace()->clearSigns();

	GC.getMapINLINE().erasePlots();

	CvMapGenerator::GetInstance().generateRandomMap();
	CvMapGenerator::GetInstance().addGameElements();

	gDLL->getEngineIFace()->RebuildAllPlots();

	CvEventReporter::getInstance().resetStatistics();

	setInitialItems();

	initScoreCalculation();
	setFinalInitialized(true);

	GC.getMapINLINE().setupGraphical();
	gDLL->getEngineIFace()->SetDirty(GlobeTexture_DIRTY_BIT, true);
	gDLL->getEngineIFace()->SetDirty(MinimapTexture_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(ColoredPlots_DIRTY_BIT, true);

	gDLL->getInterfaceIFace()->setCycleSelectionCounter(1);

	if (!isObserverNoAutosaves()) gDLL->getEngineIFace()->AutoSave(true);

	if (NO_PLAYER != getActivePlayer())
	{
		CvPlot* pPlot = GET_PLAYER(getActivePlayer()).getStartingPlot();

		if (NULL != pPlot)
		{
			gDLL->getInterfaceIFace()->lookAt(pPlot->getPoint(), CAMERALOOKAT_NORMAL);
		}
	}
}


void CvGame::uninit()
{
	SAFE_DELETE_ARRAY(m_aiShrineBuilding);
	SAFE_DELETE_ARRAY(m_aiShrineReligion);
	SAFE_DELETE_ARRAY(m_paiUnitCreatedCount);
	SAFE_DELETE_ARRAY(m_paiUnitClassCreatedCount);
	SAFE_DELETE_ARRAY(m_paiBuildingClassCreatedCount);
	SAFE_DELETE_ARRAY(m_paiProjectCreatedCount);
	SAFE_DELETE_ARRAY(m_paiForceCivicCount);
	SAFE_DELETE_ARRAY(m_paiVoteOutcome);
	SAFE_DELETE_ARRAY(m_paiReligionGameTurnFounded);
	SAFE_DELETE_ARRAY(m_paiCorporationGameTurnFounded);
	SAFE_DELETE_ARRAY(m_aiSecretaryGeneralTimer);
	SAFE_DELETE_ARRAY(m_aiVoteTimer);
	SAFE_DELETE_ARRAY(m_aiDiploVote);

	SAFE_DELETE_ARRAY(m_pabSpecialUnitValid);
	SAFE_DELETE_ARRAY(m_pabSpecialBuildingValid);
	SAFE_DELETE_ARRAY(m_abReligionSlotTaken);

	SAFE_DELETE_ARRAY(m_paHolyCity);
	SAFE_DELETE_ARRAY(m_paHeadquarters);

	m_aszDestroyedCities.clear();
	m_aszGreatPeopleBorn.clear();

	m_deals.uninit();
	m_voteSelections.uninit();
	m_votesTriggered.uninit();

	m_mapRand.uninit();
	m_sorenRand.uninit();

	clearReplayMessageMap();
	SAFE_DELETE(m_pReplayInfo);

	m_aPlotExtraYields.clear();
	m_aPlotExtraCosts.clear();
	m_mapVoteSourceReligions.clear();
	m_aeInactiveTriggers.clear();
}


// FUNCTION: reset()
// Initializes data members that are serialized.
void CvGame::reset(HandicapTypes eHandicap, bool bConstructorCall)
{
	int iI;

	//--------------------------------
	// Uninit class
	uninit();

	m_iElapsedGameTurns = 0;
	m_iStartTurn = 0;
	m_iStartYear = 0;
	m_iEstimateEndTurn = 0;
	m_iTurnSlice = 0;
	m_iCutoffSlice = 0;
	m_iNumGameTurnActive = 0;
	m_iNumCities = 0;
	m_iTotalPopulation = 0;
	m_iTradeRoutes = 0;
	m_iFreeTradeCount = 0;
	m_iNoNukesCount = 0;
	m_iNukesExploded = 0;
	m_iMaxPopulation = 0;
	m_iMaxLand = 0;
	m_iMaxTech = 0;
	m_iMaxWonders = 0;
	m_iInitPopulation = 0;
	m_iInitLand = 0;
	m_iInitTech = 0;
	m_iInitWonders = 0;
	m_iAIAutoPlay = 0;
#if ARFC_ENABLE_REPORTING
	m_bObserverAutoPlay = false;
	m_bObserverNoAutosaves = false;
	m_bObserverRevealMap = false;
#endif
	m_iCircumnavigated = -1; //Rhye

	m_uiInitialTime = 0;

	m_bScoreDirty = false;
	m_bCircumnavigated = false;
	m_bDebugMode = false;
	m_bDebugModeCache = false;
	m_bFinalInitialized = false;
	m_bPbemTurnSent = false;
	m_bHotPbemBetweenTurns = false;
	m_bPlayerOptionsSent = false;
	m_bNukesValid = false;

	m_eHandicap = eHandicap;
	m_ePausePlayer = NO_PLAYER;
	m_eBestLandUnit = NO_UNIT;
	m_eWinner = NO_TEAM;
	m_eVictory = NO_VICTORY;
	m_eGameState = GAMESTATE_ON;

	m_szScriptData = "";

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		m_aiRankPlayer[iI] = 0;
		m_aiPlayerRank[iI] = 0;
		m_aiPlayerScore[iI] = 0;
	}

	for (iI = 0; iI < MAX_TEAMS; iI++)
	{
		m_aiRankTeam[iI] = 0;
		m_aiTeamRank[iI] = 0;
		m_aiTeamScore[iI] = 0;
	}

	if (!bConstructorCall)
	{
		FAssertMsg(m_paiUnitCreatedCount==NULL, "about to leak memory, CvGame::m_paiUnitCreatedCount");
		m_paiUnitCreatedCount = new int[GC.getNumUnitInfos()];
		for (iI = 0; iI < GC.getNumUnitInfos(); iI++)
		{
			m_paiUnitCreatedCount[iI] = 0;
		}

		FAssertMsg(m_paiUnitClassCreatedCount==NULL, "about to leak memory, CvGame::m_paiUnitClassCreatedCount");
		m_paiUnitClassCreatedCount = new int[GC.getNumUnitClassInfos()];
		for (iI = 0; iI < GC.getNumUnitClassInfos(); iI++)
		{
			m_paiUnitClassCreatedCount[iI] = 0;
		}

		FAssertMsg(m_paiBuildingClassCreatedCount==NULL, "about to leak memory, CvGame::m_paiBuildingClassCreatedCount");
		m_paiBuildingClassCreatedCount = new int[GC.getNumBuildingClassInfos()];
		for (iI = 0; iI < GC.getNumBuildingClassInfos(); iI++)
		{
			m_paiBuildingClassCreatedCount[iI] = 0;
		}

		FAssertMsg(m_paiProjectCreatedCount==NULL, "about to leak memory, CvGame::m_paiProjectCreatedCount");
		m_paiProjectCreatedCount = new int[GC.getNumProjectInfos()];
		for (iI = 0; iI < GC.getNumProjectInfos(); iI++)
		{
			m_paiProjectCreatedCount[iI] = 0;
		}

		FAssertMsg(m_paiForceCivicCount==NULL, "about to leak memory, CvGame::m_paiForceCivicCount");
		m_paiForceCivicCount = new int[GC.getNumCivicInfos()];
		for (iI = 0; iI < GC.getNumCivicInfos(); iI++)
		{
			m_paiForceCivicCount[iI] = 0;
		}

		FAssertMsg(0 < GC.getNumVoteInfos(), "GC.getNumVoteInfos() is not greater than zero in CvGame::reset");
		FAssertMsg(m_paiVoteOutcome==NULL, "about to leak memory, CvGame::m_paiVoteOutcome");
		m_paiVoteOutcome = new PlayerVoteTypes[GC.getNumVoteInfos()];
		for (iI = 0; iI < GC.getNumVoteInfos(); iI++)
		{
			m_paiVoteOutcome[iI] = NO_PLAYER_VOTE;
		}

		FAssertMsg(0 < GC.getNumVoteSourceInfos(), "GC.getNumVoteSourceInfos() is not greater than zero in CvGame::reset");
		FAssertMsg(m_aiDiploVote==NULL, "about to leak memory, CvGame::m_aiDiploVote");
		m_aiDiploVote = new int[GC.getNumVoteSourceInfos()];
		for (iI = 0; iI < GC.getNumVoteSourceInfos(); iI++)
		{
			m_aiDiploVote[iI] = 0;
		}

		FAssertMsg(m_pabSpecialUnitValid==NULL, "about to leak memory, CvGame::m_pabSpecialUnitValid");
		m_pabSpecialUnitValid = new bool[GC.getNumSpecialUnitInfos()];
		for (iI = 0; iI < GC.getNumSpecialUnitInfos(); iI++)
		{
			m_pabSpecialUnitValid[iI] = false;
		}

		FAssertMsg(m_pabSpecialBuildingValid==NULL, "about to leak memory, CvGame::m_pabSpecialBuildingValid");
		m_pabSpecialBuildingValid = new bool[GC.getNumSpecialBuildingInfos()];
		for (iI = 0; iI < GC.getNumSpecialBuildingInfos(); iI++)
		{
			m_pabSpecialBuildingValid[iI] = false;
		}

		FAssertMsg(m_paiReligionGameTurnFounded==NULL, "about to leak memory, CvGame::m_paiReligionGameTurnFounded");
		m_paiReligionGameTurnFounded = new int[GC.getNumReligionInfos()];
		FAssertMsg(m_abReligionSlotTaken==NULL, "about to leak memory, CvGame::m_abReligionSlotTaken");
		m_abReligionSlotTaken = new bool[GC.getNumReligionInfos()];
		FAssertMsg(m_paHolyCity==NULL, "about to leak memory, CvGame::m_paHolyCity");
		m_paHolyCity = new IDInfo[GC.getNumReligionInfos()];
		for (iI = 0; iI < GC.getNumReligionInfos(); iI++)
		{
			m_paiReligionGameTurnFounded[iI] = -1;
			m_paHolyCity[iI].reset();
			m_abReligionSlotTaken[iI] = false;
		}

		FAssertMsg(m_paiCorporationGameTurnFounded==NULL, "about to leak memory, CvGame::m_paiCorporationGameTurnFounded");
		m_paiCorporationGameTurnFounded = new int[GC.getNumCorporationInfos()];
		m_paHeadquarters = new IDInfo[GC.getNumCorporationInfos()];
		for (iI = 0; iI < GC.getNumCorporationInfos(); iI++)
		{
			m_paiCorporationGameTurnFounded[iI] = -1;
			m_paHeadquarters[iI].reset();
		}

		FAssertMsg(m_aiShrineBuilding==NULL, "about to leak memory, CvGame::m_aiShrineBuilding");
		FAssertMsg(m_aiShrineReligion==NULL, "about to leak memory, CvGame::m_aiShrineReligion");
		m_aiShrineBuilding = new int[GC.getNumBuildingInfos()];
		m_aiShrineReligion = new int[GC.getNumBuildingInfos()];
		for (iI = 0; iI < GC.getNumBuildingInfos(); iI++)
		{
			m_aiShrineBuilding[iI] = (int) NO_BUILDING;
			m_aiShrineReligion[iI] = (int) NO_RELIGION;
		}

		FAssertMsg(m_aiSecretaryGeneralTimer==NULL, "about to leak memory, CvGame::m_aiSecretaryGeneralTimer");
		FAssertMsg(m_aiVoteTimer==NULL, "about to leak memory, CvGame::m_aiVoteTimer");
		m_aiSecretaryGeneralTimer = new int[GC.getNumVoteSourceInfos()];
		m_aiVoteTimer = new int[GC.getNumVoteSourceInfos()];
		for (iI = 0; iI < GC.getNumVoteSourceInfos(); iI++)
		{
			m_aiSecretaryGeneralTimer[iI] = 0;
			m_aiVoteTimer[iI] = 0;
		}
	}

	m_deals.removeAll();
	m_voteSelections.removeAll();
	m_votesTriggered.removeAll();
	m_iPapalPlayer = NO_PLAYER;
	m_iPapalRetryTurn = 0;
	m_iPapalFirstCouncilTurn = -1;
	m_iPapalRomeDeadline = -1;
	m_iPapalDevotionFadeStart = -1;
	m_iPapalDecisionSerial = 0;
	m_iPapalRefuser = NO_PLAYER;
	for (int iRefusal = 0; iRefusal < MAX_CIV_PLAYERS; ++iRefusal) m_aiPapalRefusalPenalties[iRefusal] = 0;
	m_papalDecisions.clear();
	m_bPapalPalaceEffects = false;
	m_bPapalCivicOverride = false;
	m_iCrusadeRegion = -1;
	m_bCrusadePeaceOverride = false;
	for (int i = 0; i < MAX_TEAMS; ++i) { m_abCrusadeParticipants[i] = false; m_abCrusadeTargets[i] = false; }
	for (int i = 0; i < MAX_PLAYERS; ++i) { m_aiCrusadePlunder[i] = 0; m_abCrusadeHolyStates[i] = false; }
	m_iCrusadeEndTurn = 0;
	for (int iReward = 0; iReward < MAX_CIV_PLAYERS; ++iReward) m_aiCrusadeRewards[iReward] = -1;

	m_mapRand.reset();
	m_sorenRand.reset();

	m_iNumSessions = 1;

    m_bShrinePopulationDirty = true;
    m_aiShrinePopulationCommerce.clear();
	m_iShrineBuildingCount = 0;
	m_iNumCultureVictoryCities = 0;
	m_eCultureVictoryCultureLevel = NO_CULTURELEVEL;

	if (!bConstructorCall)
	{
		AI_reset();
	}
}


void CvGame::initDiplomacy()
{
	PROFILE_FUNC();

	int iI, iJ;

	for (iI = 0; iI < MAX_TEAMS; iI++)
	{
		GET_TEAM((TeamTypes)iI).meet(((TeamTypes)iI), false);

		if (GET_TEAM((TeamTypes)iI).isBarbarian() || GET_TEAM((TeamTypes)iI).isMinorCiv())
		{
			//Rhye - start
			/*for (iJ = 0; iJ < MAX_CIV_TEAMS; iJ++)
			{
				if (iI != iJ)
				{
					GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)iJ), false, NO_WARPLAN);
				}
			}*/
			if (iI == INDEPENDENT || iI == INDEPENDENT2) {
				if (GET_PLAYER((PlayerTypes)CELTIA).getCivilizationType() == (CivilizationTypes)4) { //late start condition (RFCMP)
					GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)CHINA), false, NO_WARPLAN);
					GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)ARABIA), false, NO_WARPLAN);
					GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)VIKING), false, NO_WARPLAN);
				}
			}
			else if (iI == CELTIA && GET_PLAYER((PlayerTypes)CELTIA).getCivilizationType() == (CivilizationTypes)6) { //late start condition (RFCMP)
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)ROME), false, NO_WARPLAN);
				//GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)GREECE), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)ENGLAND), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)GERMANY), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)VIKING), false, NO_WARPLAN);
			}
			else if (iI == CELTIA && GET_PLAYER((PlayerTypes)CELTIA).getCivilizationType() == (CivilizationTypes)4) { //late start condition Byzantium
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)EGYPT), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)INDIA), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)BABYLONIA), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)PERSIA), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)CARTHAGE), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)ETHIOPIA), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)ARABIA), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)MONGOLIA), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)TURKEY), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)INDEPENDENT), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)INDEPENDENT2), false, NO_WARPLAN);
			}
			else {
				for (iJ = 0; iJ < MAX_CIV_TEAMS; iJ++)
				{
					if (iI != iJ)
					{
						GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)iJ), false, NO_WARPLAN);
					}
				}
			}
				//Rhye - end
		}
		//Rhye - start (uncomment only if Byzantium isn't minor)
		/*if (iI == CELTIA && !GET_PLAYER((PlayerTypes)EGYPT).isPlayable()) { //late start condition
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)ARABIA), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)TURKEY), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)MONGOLIA), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)VIKING), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)BABYLONIA), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)PERSIA), false, NO_WARPLAN);
				GET_TEAM((TeamTypes)iI).declareWar(((TeamTypes)EGYPT), false, NO_WARPLAN);
		}*/
		//Rhye - end
	}
	// Forced peace at the beginning of Advanced starts
	if (isOption(GAMEOPTION_ADVANCED_START))
	{
		CLinkList<TradeData> player1List;
		CLinkList<TradeData> player2List;
		TradeData kTradeData;
		setTradeItem(&kTradeData, TRADE_PEACE_TREATY);
		player1List.insertAtEnd(kTradeData);
		player2List.insertAtEnd(kTradeData);

		for (int iPlayer1 = 0; iPlayer1 < MAX_CIV_PLAYERS; ++iPlayer1)
		{
			CvPlayer& kLoopPlayer1 = GET_PLAYER((PlayerTypes)iPlayer1);

			if (kLoopPlayer1.isAlive())
			{
				for (int iPlayer2 = iPlayer1 + 1; iPlayer2 < MAX_CIV_PLAYERS; ++iPlayer2)
				{
					CvPlayer& kLoopPlayer2 = GET_PLAYER((PlayerTypes)iPlayer2);

					if (kLoopPlayer2.isAlive())
					{
						if (GET_TEAM(kLoopPlayer1.getTeam()).canChangeWarPeace(kLoopPlayer2.getTeam()))
						{
							implementDeal((PlayerTypes)iPlayer1, (PlayerTypes)iPlayer2, &player1List, &player2List);
						}
					}
				}
			}
		}
	}
}


void CvGame::initFreeState()
{
	bool bValid;
	int iI, iJ, iK;

	for (iI = 0; iI < GC.getNumTechInfos(); iI++)
	{
		// Starting eras grant technologies, never unit specialization.
		if (UnitMastery::unitForTech((TechTypes)iI) != NO_UNIT) continue;
		for (iJ = 0; iJ < MAX_TEAMS; iJ++)
		{
			if (GET_TEAM((TeamTypes)iJ).isAlive())
			{
				bValid = false;

				if (!bValid)
				{
					if ((GC.getHandicapInfo(getHandicapType()).isFreeTechs(iI)) ||
						  (!(GET_TEAM((TeamTypes)iJ).isHuman())&& GC.getHandicapInfo(getHandicapType()).isAIFreeTechs(iI)) ||
						  (GC.getTechInfo((TechTypes)iI).getEra() < getStartEra()))
					{
						bValid = true;
					}
				}

				if (!bValid)
				{
					for (iK = 0; iK < MAX_PLAYERS; iK++)
					{
						if (GET_PLAYER((PlayerTypes)iK).isAlive())
						{
							if (GET_PLAYER((PlayerTypes)iK).getTeam() == iJ)
							{
								if (GC.getCivilizationInfo(GET_PLAYER((PlayerTypes)iK).getCivilizationType()).isCivilizationFreeTechs(iI))
								{
									bValid = true;
									break;
								}
							}
						}
					}
				}

				GET_TEAM((TeamTypes)iJ).setHasTech(((TechTypes)iI), bValid, NO_PLAYER, false, false);
				if (bValid && GC.getTechInfo((TechTypes)iI).isMapVisible()) 
				{ 
					GC.getMapINLINE().setRevealedPlots((TeamTypes)iJ, true, true); 
				} 
			}
		}
	}

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			GET_PLAYER((PlayerTypes)iI).initFreeState();
		}
	}
}


void CvGame::initFreeUnits()
{
	int iI;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			if ((GET_PLAYER((PlayerTypes)iI).getNumUnits() == 0) && (GET_PLAYER((PlayerTypes)iI).getNumCities() == 0))
			{
				GET_PLAYER((PlayerTypes)iI).initFreeUnits();
			}
		}
	}
}


void CvGame::assignStartingPlots()
{
	PROFILE_FUNC();

	CvPlot* pPlot;
	CvPlot* pBestPlot;
	bool bStartFound;
	bool bValid;
	int iRandOffset;
	int iLoopTeam;
	int iLoopPlayer;
	int iHumanSlot;
	int iValue;
	int iBestValue;
	int iI, iJ, iK;
	
	std::vector<int> playerOrder;
	std::vector<int>::iterator playerOrderIter;

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			if (GET_PLAYER((PlayerTypes)iI).getStartingPlot() == NULL)
			{
				iBestValue = 0;
				pBestPlot = NULL;

				for (iJ = 0; iJ < GC.getMapINLINE().numPlotsINLINE(); iJ++)
				{
					gDLL->callUpdater();	// allow window updates during launch

					pPlot = GC.getMapINLINE().plotByIndexINLINE(iJ);

					if (pPlot->isStartingPlot())
					{
						bValid = true;

						for (iK = 0; iK < MAX_CIV_PLAYERS; iK++)
						{
							if (GET_PLAYER((PlayerTypes)iK).isAlive())
							{
								if (GET_PLAYER((PlayerTypes)iK).getStartingPlot() == pPlot)
								{
									bValid = false;
									break;
								}
							}
						}

						if (bValid)
						{
							iValue = (1 + getSorenRandNum(1000, "Starting Plot"));

							if (iValue > iBestValue)
							{
								iBestValue = iValue;
								pBestPlot = pPlot;
							}
						}
					}
				}

				if (pBestPlot != NULL)
				{
					GET_PLAYER((PlayerTypes)iI).setStartingPlot(pBestPlot, true);
				}
			}
		}
	}

	if (gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "assignStartingPlots"))
	{ 
		if (!gDLL->getPythonIFace()->pythonUsingDefaultImpl())
		{
			// Python override
			return;
		}
	}

	if (isTeamGame())
	{
		for (int iPass = 0; iPass < 2 * MAX_PLAYERS; ++iPass)
		{
			bStartFound = false;

			iRandOffset = getSorenRandNum(countCivTeamsAlive(), "Team Starting Plot");

			for (iI = 0; iI < MAX_CIV_TEAMS; iI++)
			{
				iLoopTeam = ((iI + iRandOffset) % MAX_CIV_TEAMS);

				if (GET_TEAM((TeamTypes)iLoopTeam).isAlive())
				{
					for (iJ = 0; iJ < MAX_CIV_PLAYERS; iJ++)
					{
						if (GET_PLAYER((PlayerTypes)iJ).isAlive())
						{
							if (GET_PLAYER((PlayerTypes)iJ).getTeam() == iLoopTeam)
							{
								if (GET_PLAYER((PlayerTypes)iJ).getStartingPlot() == NULL)
								{
									CvPlot* pStartingPlot = GET_PLAYER((PlayerTypes)iJ).findStartingPlot();

									if (NULL != pStartingPlot)
									{
										GET_PLAYER((PlayerTypes)iJ).setStartingPlot(pStartingPlot, true);
										playerOrder.push_back(iJ);
									}
									bStartFound = true;
									break;
								}
							}
						}
					}
				}
			}

			if (!bStartFound)
			{
				break;
			}
		}

		//check all players have starting plots
		for (iJ = 0; iJ < MAX_CIV_PLAYERS; iJ++)
		{
			FAssertMsg(!GET_PLAYER((PlayerTypes)iJ).isAlive() || GET_PLAYER((PlayerTypes)iJ).getStartingPlot() != NULL, "Player has no starting plot");
		}
	}
	else if (isGameMultiPlayer())
	{
		iRandOffset = getSorenRandNum(countCivPlayersAlive(), "Player Starting Plot");

		for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
		{
			iLoopPlayer = ((iI + iRandOffset) % MAX_CIV_PLAYERS);

			if (GET_PLAYER((PlayerTypes)iLoopPlayer).isAlive())
			{
				if (GET_PLAYER((PlayerTypes)iLoopPlayer).isHuman())
				{
					if (GET_PLAYER((PlayerTypes)iLoopPlayer).getStartingPlot() == NULL)
					{
						GET_PLAYER((PlayerTypes)iLoopPlayer).setStartingPlot(GET_PLAYER((PlayerTypes)iLoopPlayer).findStartingPlot(), true);
						playerOrder.push_back(iLoopPlayer);
					}
				}
			}
		}

		for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive())
			{
				if (!(GET_PLAYER((PlayerTypes)iI).isHuman()))
				{
					if (GET_PLAYER((PlayerTypes)iI).getStartingPlot() == NULL)
					{
						GET_PLAYER((PlayerTypes)iI).setStartingPlot(GET_PLAYER((PlayerTypes)iI).findStartingPlot(), true);
						playerOrder.push_back(iI);
					}
				}
			}
		}
	}
	else
	{
		iHumanSlot = range((((countCivPlayersAlive() - 1) * GC.getHandicapInfo(getHandicapType()).getStartingLocationPercent()) / 100), 0, (countCivPlayersAlive() - 1));

		for (iI = 0; iI < iHumanSlot; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive())
			{
				if (!(GET_PLAYER((PlayerTypes)iI).isHuman()))
				{
					if (GET_PLAYER((PlayerTypes)iI).getStartingPlot() == NULL)
					{
						GET_PLAYER((PlayerTypes)iI).setStartingPlot(GET_PLAYER((PlayerTypes)iI).findStartingPlot(), true);
						playerOrder.push_back(iI);
					}
				}
			}
		}

		for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive())
			{
				if (GET_PLAYER((PlayerTypes)iI).isHuman())
				{
					if (GET_PLAYER((PlayerTypes)iI).getStartingPlot() == NULL)
					{
						GET_PLAYER((PlayerTypes)iI).setStartingPlot(GET_PLAYER((PlayerTypes)iI).findStartingPlot(), true);
						playerOrder.push_back(iI);
					}
				}
			}
		}

		for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive())
			{
				if (GET_PLAYER((PlayerTypes)iI).getStartingPlot() == NULL)
				{
					GET_PLAYER((PlayerTypes)iI).setStartingPlot(GET_PLAYER((PlayerTypes)iI).findStartingPlot(), true);
					playerOrder.push_back(iI);
				}
			}
		}
	}
	
	//Now iterate over the player starts in the original order and re-place them.
	for (playerOrderIter = playerOrder.begin(); playerOrderIter != playerOrder.end(); ++playerOrderIter)
	{
		GET_PLAYER((PlayerTypes)(*playerOrderIter)).setStartingPlot(GET_PLAYER((PlayerTypes)(*playerOrderIter)).findStartingPlot(), true);
	}
}

// Swaps starting locations until we have reached the optimal closeness between teams
// (caveat: this isn't quite "optimal" because we could get stuck in local minima, but it's pretty good)

void CvGame::normalizeStartingPlotLocations()
{
	CvPlot* apNewStartPlots[MAX_CIV_PLAYERS];
	int* aaiDistances[MAX_CIV_PLAYERS];
	int aiStartingLocs[MAX_CIV_PLAYERS];
	int iI, iJ;

	// Precalculate distances between all starting positions:
	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			gDLL->callUpdater();	// allow window to update during launch
			aaiDistances[iI] = new int[iI];
			for (iJ = 0; iJ < iI; iJ++)
			{
				aaiDistances[iI][iJ] = 0;
			}
			CvPlot *pPlotI = GET_PLAYER((PlayerTypes)iI).getStartingPlot();	
			if (pPlotI != NULL)
			{
				for (iJ = 0; iJ < iI; iJ++)
				{
					if (GET_PLAYER((PlayerTypes)iJ).isAlive())
					{
						CvPlot *pPlotJ = GET_PLAYER((PlayerTypes)iJ).getStartingPlot();
						if (pPlotJ != NULL)
						{
							int iDist = GC.getMapINLINE().calculatePathDistance(pPlotI, pPlotJ);
							if (iDist == -1)
							{
								// 5x penalty for not being on the same area, or having no passable route
								iDist = 5*plotDistance(pPlotI->getX_INLINE(), pPlotI->getY_INLINE(), pPlotJ->getX_INLINE(), pPlotJ->getY_INLINE());
							}
							aaiDistances[iI][iJ] = iDist;
						}
					}
				}
			}
		}
		else
		{
			aaiDistances[iI] = NULL;
		}
	}

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		aiStartingLocs[iI] = iI; // each player starting in own location
	}

	int iBestScore = getTeamClosenessScore(aaiDistances, aiStartingLocs);
	bool bFoundSwap = true;
	while (bFoundSwap)
	{
		bFoundSwap = false;
		for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive())
			{
				for (iJ = 0; iJ < iI; iJ++)
				{
					if (GET_PLAYER((PlayerTypes)iJ).isAlive())
					{
						int iTemp = aiStartingLocs[iI];
						aiStartingLocs[iI] = aiStartingLocs[iJ];
						aiStartingLocs[iJ] = iTemp;
						int iScore = getTeamClosenessScore(aaiDistances, aiStartingLocs);
						if (iScore < iBestScore)
						{
							iBestScore = iScore;
							bFoundSwap = true;
						}
						else
						{
							// Swap them back:
							iTemp = aiStartingLocs[iI];
							aiStartingLocs[iI] = aiStartingLocs[iJ];
							aiStartingLocs[iJ] = iTemp;
						}
					}
				}
			}
		}
	} 

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		apNewStartPlots[iI] = NULL;
	} 

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			if (aiStartingLocs[iI] != iI)
			{
				apNewStartPlots[iI] = GET_PLAYER((PlayerTypes)aiStartingLocs[iI]).getStartingPlot();
			}
		}
	}

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			if (apNewStartPlots[iI] != NULL)
			{
				GET_PLAYER((PlayerTypes)iI).setStartingPlot(apNewStartPlots[iI], false);
			}
		}
	}

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		SAFE_DELETE_ARRAY(aaiDistances[iI]);
	}
}


void CvGame::normalizeAddRiver()
{
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			CvPlot* pStartingPlot = GET_PLAYER((PlayerTypes)iI).getStartingPlot();

			if (pStartingPlot != NULL)
			{
				if (!pStartingPlot->isFreshWater())
				{
					// if we will be able to add a lake, then use old river code
					if (normalizeFindLakePlot((PlayerTypes)iI) != NULL)
					{
						CvMapGenerator::GetInstance().doRiver(pStartingPlot);
					}
					// otherwise, use new river code which is much more likely to succeed
					else
					{
						CvMapGenerator::GetInstance().addRiver(pStartingPlot);
					}

					// add floodplains to any desert tiles the new river passes through
					for (int iK = 0; iK < GC.getMapINLINE().numPlotsINLINE(); iK++)
					{
						CvPlot* pPlot = GC.getMapINLINE().plotByIndexINLINE(iK);
						FAssert(pPlot != NULL);

						for (int iJ = 0; iJ < GC.getNumFeatureInfos(); iJ++)
						{
							if (GC.getFeatureInfo((FeatureTypes)iJ).isRequiresRiver())
							{
								if (pPlot->canHaveFeature((FeatureTypes)iJ))
								{
									if (GC.getFeatureInfo((FeatureTypes)iJ).getAppearanceProbability() == 10000)
									{
										if (pPlot->getBonusType() != NO_BONUS)
										{
											pPlot->setBonusType(NO_BONUS);
										}
										pPlot->setFeatureType((FeatureTypes)iJ);
										break;
									}
								}
							}
						}
					}
				}
			}
		}
	}
}


void CvGame::normalizeRemovePeaks()
{
	CvPlot* pStartingPlot;
	CvPlot* pLoopPlot;
	int iRange;
	int iDX, iDY;
	int iI;

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			pStartingPlot = GET_PLAYER((PlayerTypes)iI).getStartingPlot();

			if (pStartingPlot != NULL)
			{
				iRange = 3;

				for (iDX = -(iRange); iDX <= iRange; iDX++)
				{
					for (iDY = -(iRange); iDY <= iRange; iDY++)
					{
						pLoopPlot = plotXY(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iDX, iDY);

						if (pLoopPlot != NULL)
						{
							if (pLoopPlot->isPeak())
							{
								pLoopPlot->setPlotType(PLOT_HILLS);
							}
						}
					}
				}
			}
		}
	}
}

void CvGame::normalizeAddLakes()
{
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			CvPlot* pLakePlot = normalizeFindLakePlot((PlayerTypes)iI);
			if (pLakePlot != NULL)
			{
				pLakePlot->setPlotType(PLOT_OCEAN);
			}
		}
	}
}

CvPlot* CvGame::normalizeFindLakePlot(PlayerTypes ePlayer)
{
	if (!GET_PLAYER(ePlayer).isAlive())
	{
		return NULL;
	}

	CvPlot* pStartingPlot = GET_PLAYER(ePlayer).getStartingPlot();
	if (pStartingPlot != NULL)
	{
		if (!(pStartingPlot->isFreshWater()))
		{
			for (int iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
			{
				CvPlot* pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iJ);

				if (pLoopPlot != NULL)
				{
					if (!(pLoopPlot->isWater()))
					{
						if (!(pLoopPlot->isCoastalLand()))
						{
							if (!(pLoopPlot->isRiver()))
							{
								if (pLoopPlot->getBonusType() == NO_BONUS)
								{
									bool bStartingPlot = false;

									for (int iK = 0; iK < MAX_CIV_PLAYERS; iK++)
									{
										if (GET_PLAYER((PlayerTypes)iK).isAlive())
										{
											if (GET_PLAYER((PlayerTypes)iK).getStartingPlot() == pLoopPlot)
											{
												bStartingPlot = true;
												break;
											}
										}
									}

									if (!bStartingPlot)
									{
										return pLoopPlot;
									}
								}
							}
						}
					}
				}
			}
		}
	}

	return NULL;
}


void CvGame::normalizeRemoveBadFeatures()
{
	CvPlot* pStartingPlot;
	CvPlot* pLoopPlot;
	int iI, iJ;

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			pStartingPlot = GET_PLAYER((PlayerTypes)iI).getStartingPlot();

			if (pStartingPlot != NULL)
			{
				for (iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
					pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iJ);

					if (pLoopPlot != NULL)
					{
						if (pLoopPlot->getFeatureType() != NO_FEATURE)
						{
							if ((GC.getFeatureInfo(pLoopPlot->getFeatureType()).getYieldChange(YIELD_FOOD) <= 0) &&
								(GC.getFeatureInfo(pLoopPlot->getFeatureType()).getYieldChange(YIELD_PRODUCTION) <= 0))
							{
								pLoopPlot->setFeatureType(NO_FEATURE);
							}
						}
					}
				}
			
				int iX, iY;
				int iCityRange = CITY_PLOTS_RADIUS;
				int iExtraRange = 2;
				int iMaxRange = iCityRange + iExtraRange;
				
				for (iX = -iMaxRange; iX <= iMaxRange; iX++)
				{
					for (iY = -iMaxRange; iY <= iMaxRange; iY++)
					{
						pLoopPlot = plotXY(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iX, iY);
						if (pLoopPlot != NULL)
						{
							int iDistance = plotDistance(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), pLoopPlot->getX_INLINE(), pLoopPlot->getY_INLINE());			
							if (iDistance <= iMaxRange)
							{
								if (pLoopPlot->getFeatureType() != NO_FEATURE)
								{
									if ((GC.getFeatureInfo(pLoopPlot->getFeatureType()).getYieldChange(YIELD_FOOD) <= 0) &&
										(GC.getFeatureInfo(pLoopPlot->getFeatureType()).getYieldChange(YIELD_PRODUCTION) <= 0))
									{
										if (pLoopPlot->isWater())
										{
											if (pLoopPlot->isAdjacentToLand() || (!(iDistance == iMaxRange) && (getSorenRandNum(2, "Remove Bad Feature") == 0)))
											{
												pLoopPlot->setFeatureType(NO_FEATURE);
											}
										}
										else
										{
											if (!(iDistance == iMaxRange) && (getSorenRandNum((2 + (pLoopPlot->getBonusType() == NO_BONUS) ? 0 : 2), "Remove Bad Feature") == 0))
											{
												pLoopPlot->setFeatureType(NO_FEATURE);                                            
											}
										}
									}
								}
							}
						}
					}
				}
			}
        }
	}
}


void CvGame::normalizeRemoveBadTerrain()
{
	CvPlot* pStartingPlot;
	CvPlot* pLoopPlot;
	int iI, iK;
	int iX, iY;
	
	int iTargetFood;
	int iTargetTotal;
	int iPlotFood;
	int iPlotProduction;
	
	
	int iCityRange = CITY_PLOTS_RADIUS;
	int iExtraRange = 1;
	int iMaxRange = iCityRange + iExtraRange;

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			pStartingPlot = GET_PLAYER((PlayerTypes)iI).getStartingPlot();

			if (pStartingPlot != NULL)
			{
			    for (iX = -iMaxRange; iX <= iMaxRange; iX++)
			    {
			        for (iY = -iMaxRange; iY <= iMaxRange; iY++)
			        {
			            pLoopPlot = plotXY(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iX, iY);
                        if (pLoopPlot != NULL)
                        {
                            int iDistance = plotDistance(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), pLoopPlot->getX_INLINE(), pLoopPlot->getY_INLINE());
                            if (iDistance <= iMaxRange)
                            {
                                if (!(pLoopPlot->isWater()) && ((iDistance <= iCityRange) || (pLoopPlot->isCoastalLand()) || (0 == getSorenRandNum(1 + iDistance - iCityRange, "Map Upgrade Terrain Food"))))
                                {
                                    iPlotFood = GC.getTerrainInfo(pLoopPlot->getTerrainType()).getYield(YIELD_FOOD);
                                    iPlotProduction = GC.getTerrainInfo(pLoopPlot->getTerrainType()).getYield(YIELD_PRODUCTION);
                                    if ((iPlotFood + iPlotProduction) <= 1)
                                    {
                                        iTargetFood = 1;
                                        iTargetTotal = 1;
                                        if (pLoopPlot->getBonusType(GET_PLAYER((PlayerTypes)iI).getTeam()) != NO_BONUS)
                                        {
                                            iTargetFood = 1;
                                            iTargetTotal = 2;
                                        }
                                        else if ((iPlotFood == 1) || (iDistance <= iCityRange))
                                        {
                                            iTargetFood = 1 + getSorenRandNum(2, "Map Upgrade Terrain Food");
                                            iTargetTotal = 2;
                                        }
                                        else
                                        {
                                            iTargetFood = pLoopPlot->isCoastalLand() ? 2 : 1;
                                            iTargetTotal = 2;
                                        }
                                        
                                        for (iK = 0; iK < GC.getNumTerrainInfos(); iK++)
                                        {
                                            if (!(GC.getTerrainInfo((TerrainTypes)iK).isWater()))
                                            {
                                                if ((GC.getTerrainInfo((TerrainTypes)iK).getYield(YIELD_FOOD) >= iTargetFood) && 
                                                    (GC.getTerrainInfo((TerrainTypes)iK).getYield(YIELD_FOOD) + GC.getTerrainInfo((TerrainTypes)iK).getYield(YIELD_PRODUCTION)) == iTargetTotal)
                                                {
                                                    if ((pLoopPlot->getFeatureType() == NO_FEATURE) || GC.getFeatureInfo(pLoopPlot->getFeatureType()).isTerrain(iK))
                                                    {
                                                        pLoopPlot->setTerrainType((TerrainTypes)iK);
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
  
			            }
			        }
				}
			}
		}
	}
}


void CvGame::normalizeAddFoodBonuses()
{
	bool bIgnoreLatitude = pythonIsBonusIgnoreLatitudes();

	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			CvPlot* pStartingPlot = GET_PLAYER((PlayerTypes)iI).getStartingPlot();

			if (pStartingPlot != NULL)
			{
				int iFoodBonus = 0;
				int iGoodNatureTileCount = 0;

				for (int iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
					CvPlot* pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iJ);

					if (pLoopPlot != NULL)
					{
						BonusTypes eBonus = pLoopPlot->getBonusType(GET_PLAYER((PlayerTypes)iI).getTeam());

						if (eBonus != NO_BONUS)
						{
							if (GC.getBonusInfo(eBonus).getYieldChange(YIELD_FOOD) > 0)
							{
								if ((GC.getBonusInfo(eBonus).getTechCityTrade() == NO_TECH) || (GC.getTechInfo((TechTypes)(GC.getBonusInfo(eBonus).getTechCityTrade())).getEra() <= getStartEra()))
								{
									if (pLoopPlot->isWater())
									{
										iFoodBonus += 2;
									}
									else
									{
										iFoodBonus += 3;
									}
								}
							}
							else if (pLoopPlot->calculateBestNatureYield(YIELD_FOOD, GET_PLAYER((PlayerTypes)iI).getTeam()) >= 2)
						    {
						        iGoodNatureTileCount++;
						    }
						}
						else
						{
                            if (pLoopPlot->calculateBestNatureYield(YIELD_FOOD, GET_PLAYER((PlayerTypes)iI).getTeam()) >= 3)
						    {
						        iGoodNatureTileCount++;
						    }
						}
					}
				}
				
				int iTargetFoodBonusCount = 3;
				iTargetFoodBonusCount += (iGoodNatureTileCount == 0) ? 2 : 0;

				for (int iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
					if (iFoodBonus >= iTargetFoodBonusCount)
					{
						break;
					}

					CvPlot* pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iJ);

					if (pLoopPlot != NULL)
					{
						if (pLoopPlot != pStartingPlot)
						{
							if (pLoopPlot->getBonusType() == NO_BONUS)
							{
								for (int iK = 0; iK < GC.getNumBonusInfos(); iK++)
								{
									if (GC.getBonusInfo((BonusTypes)iK).isNormalize())
									{
										if (GC.getBonusInfo((BonusTypes)iK).getYieldChange(YIELD_FOOD) > 0)
										{
											if ((GC.getBonusInfo((BonusTypes)iK).getTechCityTrade() == NO_TECH) || (GC.getTechInfo((TechTypes)(GC.getBonusInfo((BonusTypes)iK).getTechCityTrade())).getEra() <= getStartEra()))
											{
												if (GET_TEAM(GET_PLAYER((PlayerTypes)iI).getTeam()).isHasTech((TechTypes)(GC.getBonusInfo((BonusTypes)iK).getTechReveal())))
												{
													if (pLoopPlot->canHaveBonus(((BonusTypes)iK), bIgnoreLatitude))
													{
														pLoopPlot->setBonusType((BonusTypes)iK);
														if (pLoopPlot->isWater())
														{
															iFoodBonus += 2;
														}
														else
														{
															iFoodBonus += 3;
														}
														break;
													}
												}
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
}


void CvGame::normalizeAddGoodTerrain()
{
	CvPlot* pStartingPlot;
	CvPlot* pLoopPlot;
	bool bChanged;
	int iGoodPlot;
	int iI, iJ, iK;

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			pStartingPlot = GET_PLAYER((PlayerTypes)iI).getStartingPlot();

			if (pStartingPlot != NULL)
			{
				iGoodPlot = 0;

				for (iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
					pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iJ);

					if (pLoopPlot != NULL)
					{
						if (pLoopPlot != pStartingPlot)
						{
							if ((pLoopPlot->calculateNatureYield(YIELD_FOOD, GET_PLAYER((PlayerTypes)iI).getTeam()) >= GC.getFOOD_CONSUMPTION_PER_POPULATION()) &&
								  (pLoopPlot->calculateNatureYield(YIELD_PRODUCTION, GET_PLAYER((PlayerTypes)iI).getTeam()) > 0))
							{
								iGoodPlot++;
							}
						}
					}
				}

				for (iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
					if (iGoodPlot >= 4)
					{
						break;
					}

					pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iJ);

					if (pLoopPlot != NULL)
					{
						if (pLoopPlot != pStartingPlot)
						{
							if (!(pLoopPlot->isWater()))
							{
								if (!(pLoopPlot->isHills()))
								{
									if (pLoopPlot->getBonusType() == NO_BONUS)
									{
										bChanged = false;

										if (pLoopPlot->calculateNatureYield(YIELD_FOOD, GET_PLAYER((PlayerTypes)iI).getTeam()) < GC.getFOOD_CONSUMPTION_PER_POPULATION())
										{
											for (iK = 0; iK < GC.getNumTerrainInfos(); iK++)
											{
												if (!(GC.getTerrainInfo((TerrainTypes)iK).isWater()))
												{
													if (GC.getTerrainInfo((TerrainTypes)iK).getYield(YIELD_FOOD) >= GC.getFOOD_CONSUMPTION_PER_POPULATION())
													{
														pLoopPlot->setTerrainType((TerrainTypes)iK);
														bChanged = true;
														break;
													}
												}
											}
										}

										if (pLoopPlot->calculateNatureYield(YIELD_PRODUCTION, GET_PLAYER((PlayerTypes)iI).getTeam()) == 0)
										{
											for (iK = 0; iK < GC.getNumFeatureInfos(); iK++)
											{
												if ((GC.getFeatureInfo((FeatureTypes)iK).getYieldChange(YIELD_FOOD) >= 0) &&
													  (GC.getFeatureInfo((FeatureTypes)iK).getYieldChange(YIELD_PRODUCTION) > 0))
												{
													if (GC.getFeatureInfo((FeatureTypes)iK).isTerrain(pLoopPlot->getTerrainType()))
													{
														pLoopPlot->setFeatureType((FeatureTypes)iK);
														bChanged = true;
														break;
													}
												}
											}
										}

										if (bChanged)
										{
											iGoodPlot++;
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
}


void CvGame::normalizeAddExtras()
{
	bool bIgnoreLatitude = pythonIsBonusIgnoreLatitudes();

	int iTotalValue = 0;
	int iPlayerCount = 0;
	int iBestValue = 0;
	int iWorstValue = MAX_INT;

	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			CvPlot* pStartingPlot = GET_PLAYER((PlayerTypes)iI).getStartingPlot();

			if (pStartingPlot != NULL)
			{
				int iValue = GET_PLAYER((PlayerTypes)iI).AI_foundValue(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), -1, true);
				iTotalValue += iValue;
                iPlayerCount++;
                
                iBestValue = std::max(iValue, iBestValue);
                iWorstValue = std::min(iValue, iWorstValue);
			}
		}
	}

	//iTargetValue = (iTotalValue + iBestValue) / (iPlayerCount + 1);
	int iTargetValue = (iBestValue * 4) / 5;
	
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			gDLL->callUpdater();	// allow window to update during launch
			CvPlot* pStartingPlot = GET_PLAYER((PlayerTypes)iI).getStartingPlot();

			if (pStartingPlot != NULL)
			{
                int iCount = 0;
				int iFeatureCount = 0;
				int aiShuffle[NUM_CITY_PLOTS];
				shuffleArray(aiShuffle, NUM_CITY_PLOTS, getMapRand());

				for (int iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
					if (GET_PLAYER((PlayerTypes)iI).AI_foundValue(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), -1, true) >= iTargetValue)
					{
						break;
					}
					if (getSorenRandNum((iCount + 2), "Setting Feature Type") <= 1)
					{
						CvPlot* pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), aiShuffle[iJ]);

						if (pLoopPlot != NULL)
						{
							if (pLoopPlot != pStartingPlot)
							{
								if (pLoopPlot->getBonusType() == NO_BONUS)
								{
									if (pLoopPlot->getFeatureType() == NO_FEATURE)
									{
										for (int iK = 0; iK < GC.getNumFeatureInfos(); iK++)
										{
											if ((GC.getFeatureInfo((FeatureTypes)iK).getYieldChange(YIELD_FOOD) + GC.getFeatureInfo((FeatureTypes)iK).getYieldChange(YIELD_PRODUCTION)) > 0)
											{
												if (pLoopPlot->canHaveFeature((FeatureTypes)iK))
												{
													pLoopPlot->setFeatureType((FeatureTypes)iK);
													iCount++;
													break;
												}
											}
										}
									}
									
									iFeatureCount += (pLoopPlot->getFeatureType() != NO_FEATURE) ? 1 : 0;
								}
							}
						}
					}
				}
				
				int iCoastFoodCount = 0;
				int iOceanFoodCount = 0;
				int iOtherCount = 0;
				int iWaterCount = 0;
				for (int iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
					CvPlot* pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iJ);
					if (pLoopPlot != NULL)
					{
						if (pLoopPlot != pStartingPlot)
						{
							if (pLoopPlot->isWater())
							{
								iWaterCount++;
								if (pLoopPlot->getBonusType() != NO_BONUS)
								{
									if (pLoopPlot->isAdjacentToLand())
									{
										iCoastFoodCount++;
									}
									else
									{
										iOceanFoodCount++;                                        
									}
								}
							}
							else
							{
								if (pLoopPlot->getBonusType() != NO_BONUS)
								{
									iOtherCount++;
								}
							}
						}
					}
				}
				
			    bool bLandBias = (iWaterCount > NUM_CITY_PLOTS / 2);
                
                shuffleArray(aiShuffle, NUM_CITY_PLOTS, getMapRand());                

				for (int iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
				    CvPlot* pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), aiShuffle[iJ]);

                    if ((pLoopPlot != NULL) && (pLoopPlot != pStartingPlot))
                    {
                        if (getSorenRandNum(((bLandBias && pLoopPlot->isWater()) ? 2 : 1), "Placing Bonuses") == 0)
                        {
                        	if ((iOtherCount * 3 + iOceanFoodCount * 2 + iCoastFoodCount * 2) >= 12)
                        	{
                        		break;
                        	}
                        	
                            if (GET_PLAYER((PlayerTypes)iI).AI_foundValue(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), -1, true) >= iTargetValue)
                            {
                                break;
                            }

						    bool bCoast = (pLoopPlot->isWater() && pLoopPlot->isAdjacentToLand());
						    bool bOcean = (pLoopPlot->isWater() && !bCoast);
							if ((pLoopPlot != pStartingPlot)
                                && !(bCoast && (iCoastFoodCount > 2))
                                && !(bOcean && (iOceanFoodCount > 2)))
							{
								for (int iPass = 0; iPass < 2; iPass++)
								{
									if (pLoopPlot->getBonusType() == NO_BONUS)
									{
										for (int iK = 0; iK < GC.getNumBonusInfos(); iK++)
										{
											if (GC.getBonusInfo((BonusTypes)iK).isNormalize())
											{
											    //???no bonuses with negative yields?
												if ((GC.getBonusInfo((BonusTypes)iK).getYieldChange(YIELD_FOOD) >= 0) &&
													  (GC.getBonusInfo((BonusTypes)iK).getYieldChange(YIELD_PRODUCTION) >= 0))
												{
													if ((GC.getBonusInfo((BonusTypes)iK).getTechCityTrade() == NO_TECH) || (GC.getTechInfo((TechTypes)(GC.getBonusInfo((BonusTypes)iK).getTechCityTrade())).getEra() <= getStartEra()))
													{
														if (GET_TEAM(GET_PLAYER((PlayerTypes)iI).getTeam()).isHasTech((TechTypes)(GC.getBonusInfo((BonusTypes)iK).getTechReveal())))
														{
															if ((iPass == 0) ? CvMapGenerator::GetInstance().canPlaceBonusAt(((BonusTypes)iK), pLoopPlot->getX(), pLoopPlot->getY(), bIgnoreLatitude) : pLoopPlot->canHaveBonus(((BonusTypes)iK), bIgnoreLatitude))
															{
																pLoopPlot->setBonusType((BonusTypes)iK);
																iCoastFoodCount += bCoast ? 1 : 0;
																iOceanFoodCount += bOcean ? 1 : 0;
																iOtherCount += !(bCoast || bOcean) ? 1 : 0;
																break;
															}
														}
													}
												}
											}
										}
										
										if (bLandBias && !pLoopPlot->isWater() && pLoopPlot->getBonusType() == NO_BONUS)
										{
											if (((iFeatureCount > 4) && (pLoopPlot->getFeatureType() != NO_FEATURE))
												&& ((iCoastFoodCount + iOceanFoodCount) > 2))
											{
												if (getSorenRandNum(2, "Clear feature to add bonus") == 0)
												{
												pLoopPlot->setFeatureType(NO_FEATURE);

													for (iK = 0; iK < GC.getNumBonusInfos(); iK++)
													{
														if (GC.getBonusInfo((BonusTypes)iK).isNormalize())
														{
															//???no bonuses with negative yields?
															if ((GC.getBonusInfo((BonusTypes)iK).getYieldChange(YIELD_FOOD) >= 0) &&
																  (GC.getBonusInfo((BonusTypes)iK).getYieldChange(YIELD_PRODUCTION) >= 0))
															{
																if ((GC.getBonusInfo((BonusTypes)iK).getTechCityTrade() == NO_TECH) || (GC.getTechInfo((TechTypes)(GC.getBonusInfo((BonusTypes)iK).getTechCityTrade())).getEra() <= getStartEra()))
																{
																	if ((iPass == 0) ? CvMapGenerator::GetInstance().canPlaceBonusAt(((BonusTypes)iK), pLoopPlot->getX(), pLoopPlot->getY(), bIgnoreLatitude) : pLoopPlot->canHaveBonus(((BonusTypes)iK), bIgnoreLatitude))
																	{
																		pLoopPlot->setBonusType((BonusTypes)iK);
																		iOtherCount++;
																		break;
																	}
																}
															}
														}
													}
												}
											}										
										}
									}
								}
							}
						}
					}
				}
				
				shuffleArray(aiShuffle, NUM_CITY_PLOTS, getMapRand());

				for (iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
					if (GET_PLAYER((PlayerTypes)iI).AI_foundValue(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), -1, true) >= iTargetValue)
					{
						break;
					}
				
					CvPlot* pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), aiShuffle[iJ]);

					if (pLoopPlot != NULL)
					{
						if (pLoopPlot != pStartingPlot)
						{
							if (pLoopPlot->getBonusType() == NO_BONUS)
							{
								if (pLoopPlot->getFeatureType() == NO_FEATURE)
								{
									for (int iK = 0; iK < GC.getNumFeatureInfos(); iK++)
									{
										if ((GC.getFeatureInfo((FeatureTypes)iK).getYieldChange(YIELD_FOOD) + GC.getFeatureInfo((FeatureTypes)iK).getYieldChange(YIELD_PRODUCTION)) > 0)
										{
											if (pLoopPlot->canHaveFeature((FeatureTypes)iK))
											{
												pLoopPlot->setFeatureType((FeatureTypes)iK);
												break;
											}
										}
									}
								}
							}
						}
					}
				}
				
				int iHillsCount = 0;
				
				for (int iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
					CvPlot* pLoopPlot =plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), iJ);
					if (pLoopPlot != NULL)
					{
						if (pLoopPlot->isHills())
						{
							iHillsCount++;
						}
					}
				}
				shuffleArray(aiShuffle, NUM_CITY_PLOTS, getMapRand());
				for (int iJ = 0; iJ < NUM_CITY_PLOTS; iJ++)
				{
					if (iHillsCount >= 3)
					{
						break;
					}
					CvPlot* pLoopPlot = plotCity(pStartingPlot->getX_INLINE(), pStartingPlot->getY_INLINE(), aiShuffle[iJ]);
					if (pLoopPlot != NULL)
					{
						if (!pLoopPlot->isWater())
						{
							if (!pLoopPlot->isHills())
							{
								if ((pLoopPlot->getFeatureType() == NO_FEATURE) ||
									!GC.getFeatureInfo(pLoopPlot->getFeatureType()).isRequiresFlatlands())
								{
									if ((pLoopPlot->getBonusType() == NO_BONUS) ||
										GC.getBonusInfo(pLoopPlot->getBonusType()).isHills())
									{
										pLoopPlot->setPlotType(PLOT_HILLS, false, true);									
										iHillsCount++;
									}
								}
							}
						}
					}
				}
			}
		}
	}
}


void CvGame::normalizeStartingPlots()
{
	PROFILE_FUNC();

	if (!(GC.getInitCore().getWBMapScript()) || GC.getInitCore().getWBMapNoPlayers())
	{
		if (!gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "normalizeStartingPlotLocations", NULL)  || gDLL->getPythonIFace()->pythonUsingDefaultImpl())
		{
			normalizeStartingPlotLocations();
		}
	}

	if (GC.getInitCore().getWBMapScript())
	{
		return;
	}

	if (!gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "normalizeAddRiver", NULL)  || gDLL->getPythonIFace()->pythonUsingDefaultImpl())
	{
		normalizeAddRiver();
	}

	if (!gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "normalizeRemovePeaks", NULL)  || gDLL->getPythonIFace()->pythonUsingDefaultImpl())
	{
		normalizeRemovePeaks();
	}

	if (!gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "normalizeAddLakes", NULL)  || gDLL->getPythonIFace()->pythonUsingDefaultImpl())
	{
		normalizeAddLakes();
	}

	if (!gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "normalizeRemoveBadFeatures", NULL)  || gDLL->getPythonIFace()->pythonUsingDefaultImpl())
	{
		normalizeRemoveBadFeatures();
	}

	if (!gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "normalizeRemoveBadTerrain", NULL)  || gDLL->getPythonIFace()->pythonUsingDefaultImpl())
	{
		normalizeRemoveBadTerrain();
	}

	if (!gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "normalizeAddFoodBonuses", NULL)  || gDLL->getPythonIFace()->pythonUsingDefaultImpl())
	{
		normalizeAddFoodBonuses();
	}

	if (!gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "normalizeAddGoodTerrain", NULL)  || gDLL->getPythonIFace()->pythonUsingDefaultImpl())
	{
		normalizeAddGoodTerrain();
	}

	if (!gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "normalizeAddExtras", NULL)  || gDLL->getPythonIFace()->pythonUsingDefaultImpl())
	{
		normalizeAddExtras();
	}
}

// For each of n teams, let the closeness score for that team be the average distance of an edge between two players on that team.
// This function calculates the closeness score for each team and returns the sum of those n scores.
// The lower the result, the better "clumped" the players' starting locations are.
//
// Note: for the purposes of this function, player i will be assumed to start in the location of player aiStartingLocs[i] 

int CvGame::getTeamClosenessScore(int** aaiDistances, int* aiStartingLocs)
{
	int iScore = 0;

	for (int iTeam = 0; iTeam < MAX_CIV_TEAMS; iTeam++)
	{
		if (GET_TEAM((TeamTypes)iTeam).isAlive())
		{
			int iTeamTotalDist = 0;
			int iNumEdges = 0;
			for (int iPlayer = 0; iPlayer < MAX_CIV_PLAYERS; iPlayer++)
			{
				if (GET_PLAYER((PlayerTypes)iPlayer).isAlive())
				{
					if (GET_PLAYER((PlayerTypes)iPlayer).getTeam() == (TeamTypes)iTeam)
					{
						for (int iOtherPlayer = 0; iOtherPlayer < iPlayer; iOtherPlayer++)
						{
							if (GET_PLAYER((PlayerTypes)iOtherPlayer).getTeam() == (TeamTypes)iTeam)
							{
								// Add the edge between these two players that are on the same team
								iNumEdges++;
								int iPlayerStart = aiStartingLocs[iPlayer];
								int iOtherPlayerStart = aiStartingLocs[iOtherPlayer];

								if (iPlayerStart < iOtherPlayerStart) // Make sure that iPlayerStart > iOtherPlayerStart
								{
									int iTemp = iPlayerStart;
									iPlayerStart = iOtherPlayerStart;
									iOtherPlayerStart = iTemp;
								}
								else if (iPlayerStart == iOtherPlayerStart)
								{
									FAssertMsg(false, "Two players are (hypothetically) assigned to the same starting location!");
								}
								iTeamTotalDist += aaiDistances[iPlayerStart][iOtherPlayerStart];
							}
						}
					}
				}
			}

			int iTeamScore;
			if (iNumEdges == 0)
			{
				iTeamScore = 0;
			}
			else
			{
				iTeamScore = iTeamTotalDist/iNumEdges; // the avg distance between team edges is the team score
			}

			iScore += iTeamScore; 
		}
	}
	return iScore;
}


void CvGame::update()
{
	OBSERVER_PERFORMANCE("CvGame::update");
	PROFILE("CvGame::update");
	//logMsg("update"); //Rhye
	if (!gDLL->GetWorldBuilderMode() || isInAdvancedStart())
	{
		sendPlayerOptions();

		// sample generic event
		//Rhye - start (this must not be commented as in Kael's mod)
		CyArgsList pyArgs;
		pyArgs.add(getTurnSlice());
		CvEventReporter::getInstance().genericEvent("gameUpdate", pyArgs.makeFunctionArgs());

		if (getTurnSlice() == 0)
		{
			if (!isObserverNoAutosaves()) gDLL->getEngineIFace()->AutoSave(true);
		}

		if (getNumGameTurnActive() == 0)
		{
			if (!isPbem() || !getPbemTurnSent())
			{
				doTurn();
			}
		}

		updateScore();

		updateWar();

		updateMoves();

		updateTimers();

		updateTurnTimer();

		AI_updateAssignWork();

		testAlive();

		if (!isObserverAutoPlay() && (getAIAutoPlay() == 0) && !(gDLL->GetAutorun()) && GAMESTATE_EXTENDED != getGameState())
		{
			if (countHumanPlayersAlive() == 0)
			{
				setGameState(GAMESTATE_OVER);
			}
		}

		changeTurnSlice(1);

		if (NO_PLAYER != getActivePlayer() && GET_PLAYER(getActivePlayer()).getAdvancedStartPoints() >= 0 && !gDLL->getInterfaceIFace()->isInAdvancedStart())
		{
			gDLL->getInterfaceIFace()->setInAdvancedStart(true);
			gDLL->getInterfaceIFace()->setWorldBuilder(true);
		}
		//RFCMP
		/*
		//Rhye - start switch - Version B (late human starts)
		int iHuman = MAX_PLAYERS;
		for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive())
			{
				if (GET_PLAYER((PlayerTypes)iI).isHuman())
				{
					iHuman = iI;
					break;
				}
			}
		}
		int iHuman = getActivePlayer();

		//an IF here causes a CRASH
		switch (iHuman)
		{
		case EGYPT:
			break;
		case INDIA:
			break;
		case CHINA:
			break;
		case BABYLONIA:
			break;
		case JAPAN:
			if (GET_PLAYER((PlayerTypes)CELTIA).getCivilizationType() == (CivilizationTypes)4 || GET_PLAYER((PlayerTypes)INDEPENDENT).getLeader() == (LeaderHeadTypes)5) //late start condition 800BC
				break;
		case VIKING:
			if (GET_PLAYER((PlayerTypes)CELTIA).getCivilizationType() == (CivilizationTypes)4) //late start condition
				break;
		case ARABIA:
			if (GET_PLAYER((PlayerTypes)CELTIA).getCivilizationType() == (CivilizationTypes)4) //late start condition
				break;
		case GREECE:
			if (GET_PLAYER((PlayerTypes)INDEPENDENT).getLeader() == (LeaderHeadTypes)5) //late start condition 800BC
				break;
		case PERSIA:
			if (GET_PLAYER((PlayerTypes)INDEPENDENT).getLeader() == (LeaderHeadTypes)5) //late start condition 800BC
				break;
		case CARTHAGE:
			if (GET_PLAYER((PlayerTypes)INDEPENDENT).getLeader() == (LeaderHeadTypes)5) //late start condition 800BC
				break;
		case ROME:
			if (GET_PLAYER((PlayerTypes)INDEPENDENT).getLeader() == (LeaderHeadTypes)5) //late start condition 800BC
				break;
		case ETHIOPIA:
		case MAYA:		
		case KHMER:
		case SPAIN:
		case FRANCE:
		case ENGLAND:
		case GERMANY:
		case RUSSIA:
		case NETHERLANDS:
		case MALI:
		case TURKEY:
		case PORTUGAL:
		case INCA:
		case MONGOLIA:
		case AZTEC:
		case AMERICA:
			if (getGameTurn() == 0 || (getGameTurn() == 181 && GET_PLAYER((PlayerTypes)CELTIA).getCivilizationType() == (CivilizationTypes)4)) //late start condition
			{
				setAIAutoPlay(1);
			}
			else if (getGameTurn() <= startingTurn[iHuman])
			{
				setAIAutoPlayCatapult(1);
			}
			break;
		}*/
		//Rhye - end
	}
}


void CvGame::updateScore(bool bForce)
{
	OBSERVER_PERFORMANCE("CvGame::updateScore");
	bool abPlayerScored[MAX_CIV_PLAYERS];
	bool abTeamScored[MAX_CIV_TEAMS];
	int iScore;
	int iBestScore;
	PlayerTypes eBestPlayer;
	TeamTypes eBestTeam;
	int iI, iJ, iK;

	if (!isScoreDirty() && !bForce)
	{
		return;
	}

	setScoreDirty(false);

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		abPlayerScored[iI] = false;
	}

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		iBestScore = MIN_INT;
		eBestPlayer = NO_PLAYER;

		for (iJ = 0; iJ < MAX_CIV_PLAYERS; iJ++)
		{
			if (!abPlayerScored[iJ])
			{
				iScore = GET_PLAYER((PlayerTypes)iJ).calculateScore(false);

				if (iScore >= iBestScore)
				{
					iBestScore = iScore;
					eBestPlayer = (PlayerTypes)iJ;
				}
			}
		}

		abPlayerScored[eBestPlayer] = true;

		setRankPlayer(iI, eBestPlayer);
		setPlayerRank(eBestPlayer, iI);
		setPlayerScore(eBestPlayer, iBestScore);
		GET_PLAYER(eBestPlayer).updateScoreHistory(getGameTurn(), iBestScore);
	}

	for (iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		abTeamScored[iI] = false;
	}

	for (iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		iBestScore = MIN_INT;
		eBestTeam = NO_TEAM;

		for (iJ = 0; iJ < MAX_CIV_TEAMS; iJ++)
		{
			if (!abTeamScored[iJ])
			{
				iScore = 0;

				for (iK = 0; iK < MAX_CIV_PLAYERS; iK++)
				{
					if (GET_PLAYER((PlayerTypes)iK).getTeam() == iJ)
					{
						iScore += getPlayerScore((PlayerTypes)iK);
					}
				}

				if (iScore >= iBestScore)
				{
					iBestScore = iScore;
					eBestTeam = (TeamTypes)iJ;
				}
			}
		}

		abTeamScored[eBestTeam] = true;

		setRankTeam(iI, eBestTeam);
		setTeamRank(eBestTeam, iI);
		setTeamScore(eBestTeam, iBestScore);
	}
}

void CvGame::updatePlotGroups()
{
	PROFILE_FUNC();

	int iI;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			GET_PLAYER((PlayerTypes)iI).updatePlotGroups();
		}
	}
}


void CvGame::updateBuildingCommerce()
{
	int iI;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			GET_PLAYER((PlayerTypes)iI).updateBuildingCommerce();
		}
	}
}


void CvGame::updateCitySight(bool bIncrement)
{
	int iI;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			GET_PLAYER((PlayerTypes)iI).updateCitySight(bIncrement, false);
		}
	}

	updatePlotGroups();
}



namespace
{
struct FoodTradeRequest
{
    CvCity* supplier;
    CvCity* recipient;
    CvCity* routeOrigin;
    int demandTimes100;
    int allocated;
    __int64 remainder;
};

bool foodCityOrder(const CvCity* a, const CvCity* b)
{
    if (a->getOwnerINLINE() != b->getOwnerINLINE()) return a->getOwnerINLINE() < b->getOwnerINLINE();
    return a->getID() < b->getID();
}
}

void CvGame::updateFoodTrade()
{
	OBSERVER_PERFORMANCE("CvGame::updateFoodTrade");
    // One synchronized snapshot for all players, before anyone's city growth.
    // Only actual selected routes count; reciprocal routes form one food link.
    std::vector<CvCity*> cities;
    std::vector<FoodTradeRequest> requests;
    for (int iPlayer = 0; iPlayer < MAX_PLAYERS; ++iPlayer)
    {
        int iLoop;
        for (CvCity* pCity = GET_PLAYER((PlayerTypes)iPlayer).firstCity(&iLoop); pCity != NULL;
            pCity = GET_PLAYER((PlayerTypes)iPlayer).nextCity(&iLoop))
        {
            pCity->clearFoodTrade();
            cities.push_back(pCity);
        }
    }
    std::sort(cities.begin(), cities.end(), foodCityOrder);
    for (unsigned int i = 0; i < cities.size(); ++i)
    {
        CvCity* pOrigin = cities[i];
        if (pOrigin->isDisorder() || pOrigin->isPlundered()) continue;
        for (int iRoute = 0; iRoute < pOrigin->getTradeRoutes(); ++iRoute)
        {
            CvCity* pPartner = pOrigin->getTradeCity(iRoute);
            if (pPartner == NULL || pPartner == pOrigin || pPartner->isDisorder() || pPartner->isPlundered()) continue;
            if (!GET_PLAYER(pOrigin->getOwnerINLINE()).canHaveTradeRoutesWith(pPartner->getOwnerINLINE())) continue;
            if (pOrigin->getTeam() != pPartner->getTeam() && !GET_TEAM(pOrigin->getTeam()).isFreeTrade(pPartner->getTeam())) continue;
            const int iInfrastructureEfficiency = pOrigin->getTradeInfrastructureEfficiency(pPartner);
            if (iInfrastructureEfficiency <= 0) continue;
            // Infrastructure validity is fixed for shipments allocated here.
            // Food queries recheck route membership and diplomacy, not terrain.
            const int iTotalPressure = pOrigin->getFoodTradePressure(pPartner);
            if (iTotalPressure == 0) continue;
            CvCity* pSupplier = iTotalPressure > 0 ? pOrigin : pPartner;
            CvCity* pRecipient = iTotalPressure > 0 ? pPartner : pOrigin;
            const int iValue = pOrigin->calculateTradeYield(YIELD_COMMERCE, pOrigin->calculateTradeProfit(pPartner));
            const int iDemand = pOrigin->getFoodTradeDemand(pPartner, iValue) * iInfrastructureEfficiency / 100;
            if (iDemand <= 0) continue;
            unsigned int j;
            for (j = 0; j < requests.size(); ++j)
                if (requests[j].supplier == pSupplier && requests[j].recipient == pRecipient) break;
            if (j == requests.size())
            {
                FoodTradeRequest request;
                request.supplier = pSupplier;
                request.recipient = pRecipient;
                request.routeOrigin = pOrigin;
                request.demandTimes100 = iDemand;
                request.allocated = 0;
                request.remainder = 0;
                requests.push_back(request);
            }
            else if (iDemand > requests[j].demandTimes100)
            {
                requests[j].demandTimes100 = iDemand;
                requests[j].routeOrigin = pOrigin;
            }
        }
    }
    for (unsigned int i = 0; i < cities.size(); ++i)
    {
        CvCity* pSupplier = cities[i];
        __int64 iDemandTotal = 0;
        for (unsigned int j = 0; j < requests.size(); ++j)
            if (requests[j].supplier == pSupplier) iDemandTotal += requests[j].demandTimes100;
        if (iDemandTotal == 0) continue;
        int iBudget = (int)std::min((__int64)pSupplier->getFoodExportLimit(), iDemandTotal / 100);
        int iAssigned = 0;
        for (unsigned int j = 0; j < requests.size(); ++j)
        {
            FoodTradeRequest& r = requests[j];
            if (r.supplier != pSupplier) continue;
            __int64 iShare = (__int64)iBudget * r.demandTimes100;
            r.allocated = (int)(iShare / iDemandTotal);
            r.remainder = iShare % iDemandTotal;
            iAssigned += r.allocated;
        }
        // Largest remainders, ties in stable city/route order; no RNG or floats.
        while (iAssigned < iBudget)
        {
            int iBest = -1;
            for (unsigned int j = 0; j < requests.size(); ++j)
                if (requests[j].supplier == pSupplier && requests[j].remainder >= 0 &&
                    (iBest < 0 || requests[j].remainder > requests[iBest].remainder)) iBest = j;
            if (iBest < 0) break;
            ++requests[iBest].allocated;
            requests[iBest].remainder = -1;
            ++iAssigned;
        }
    }
    for (unsigned int i = 0; i < requests.size(); ++i)
    {
        FoodTradeRequest& r = requests[i];
        if (r.allocated == 0) continue;
        r.supplier->addFoodTrade(r.recipient, r.routeOrigin == r.supplier, -r.allocated);
        r.recipient->addFoodTrade(r.supplier, r.routeOrigin == r.recipient, r.allocated);
    }
    gDLL->getInterfaceIFace()->setDirty(CityScreen_DIRTY_BIT, true);
}

void CvGame::updateTradeRoutes()
{
	OBSERVER_PERFORMANCE("CvGame::updateTradeRoutes");
	int iI;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			GET_PLAYER((PlayerTypes)iI).updateTradeRoutes();
		}
	}
}


void CvGame::testExtendedGame()
{
	int iI;

	if (getGameState() != GAMESTATE_OVER)
	{
		return;
	}

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			if (GET_PLAYER((PlayerTypes)iI).isHuman())
			{
				if (GET_PLAYER((PlayerTypes)iI).isExtendedGame())
				{
					setGameState(GAMESTATE_EXTENDED);
					break;
				}
			}
		}
	}
}


void CvGame::cityPushOrder(CvCity* pCity, OrderTypes eOrder, int iData, bool bAlt, bool bShift, bool bCtrl) const
{
	if (pCity->getProduction() > 0)
	{
		CvMessageControl::getInstance().sendPushOrder(pCity->getID(), eOrder, iData, bAlt, bShift, !bShift);
	}
	else if ((eOrder == ORDER_TRAIN) && (pCity->getProductionUnit() == iData))
	{
		CvMessageControl::getInstance().sendPushOrder(pCity->getID(), eOrder, iData, bAlt, !bCtrl, bCtrl);
	}
	else
	{
		CvMessageControl::getInstance().sendPushOrder(pCity->getID(), eOrder, iData, bAlt, bShift, bCtrl);
	}
}


void CvGame::selectUnit(CvUnit* pUnit, bool bClear, bool bToggle, bool bSound) const
{
	PROFILE_FUNC();

	CLLNode<IDInfo>* pEntityNode;
	CvSelectionGroup* pSelectionGroup;
	bool bSelectGroup;
	bool bGroup;

	if (gDLL->getInterfaceIFace()->getHeadSelectedUnit() == NULL)
	{
		bSelectGroup = true;
	}
	else if (gDLL->getInterfaceIFace()->getHeadSelectedUnit()->getGroup() != pUnit->getGroup())
	{
		bSelectGroup = true;
	}
	else if (pUnit->IsSelected() && !(gDLL->getInterfaceIFace()->mirrorsSelectionGroup()))
	{
		bSelectGroup = !bToggle;
	}
	else
	{
		bSelectGroup = false;
	}

	gDLL->getInterfaceIFace()->clearSelectedCities();

	if (bClear)
	{
		gDLL->getInterfaceIFace()->clearSelectionList();
		bGroup = false;
	}
	else
	{
		bGroup = gDLL->getInterfaceIFace()->mirrorsSelectionGroup();
	}

	if (bSelectGroup)
	{
		pSelectionGroup = pUnit->getGroup();

		gDLL->getInterfaceIFace()->selectionListPreChange();

		pEntityNode = pSelectionGroup->headUnitNode();

		while (pEntityNode != NULL)
		{
			FAssertMsg(::getUnit(pEntityNode->m_data), "null entity in selection group");
			gDLL->getInterfaceIFace()->insertIntoSelectionList(::getUnit(pEntityNode->m_data), false, bToggle, bGroup, bSound, true);

			pEntityNode = pSelectionGroup->nextUnitNode(pEntityNode);
		}

		gDLL->getInterfaceIFace()->selectionListPostChange();
	}
	else
	{
		gDLL->getInterfaceIFace()->insertIntoSelectionList(pUnit, false, bToggle, bGroup, bSound);
	}

	gDLL->getInterfaceIFace()->makeSelectionListDirty();
}


void CvGame::selectGroup(CvUnit* pUnit, bool bShift, bool bCtrl, bool bAlt) const
{
	PROFILE_FUNC();

	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pUnitPlot;
	bool bGroup;

	FAssertMsg(pUnit != NULL, "pUnit == NULL unexpectedly");

	if (bAlt || bCtrl)
	{
		gDLL->getInterfaceIFace()->clearSelectedCities();

		if (!bShift)
		{
			gDLL->getInterfaceIFace()->clearSelectionList();
			bGroup = true;
		}
		else
		{
			bGroup = gDLL->getInterfaceIFace()->mirrorsSelectionGroup();
		}

		pUnitPlot = pUnit->plot();

		pUnitNode = pUnitPlot->headUnitNode();

		gDLL->getInterfaceIFace()->selectionListPreChange();

		while (pUnitNode != NULL)
		{
			pLoopUnit = ::getUnit(pUnitNode->m_data);
			pUnitNode = pUnitPlot->nextUnitNode(pUnitNode);

			if (pLoopUnit->getOwnerINLINE() == getActivePlayer())
			{
				if (pLoopUnit->canMove())
				{
					if (!isMPOption(MPOPTION_SIMULTANEOUS_TURNS) || getTurnSlice() - pLoopUnit->getLastMoveTurn() > GC.getDefineINT("MIN_TIMER_UNIT_DOUBLE_MOVES"))
					{
						if (bAlt || (pLoopUnit->getUnitType() == pUnit->getUnitType()))
						{
							gDLL->getInterfaceIFace()->insertIntoSelectionList(pLoopUnit, false, false, bGroup, false, true);
						}
					}
				}
			}
		}

		gDLL->getInterfaceIFace()->selectionListPostChange();
	}
	else
	{
		gDLL->getInterfaceIFace()->selectUnit(pUnit, !bShift, bShift, true);
	}
}


void CvGame::selectAll(CvPlot* pPlot) const
{
	CvUnit* pSelectUnit;
	CvUnit* pCenterUnit;

	pSelectUnit = NULL;

	if (pPlot != NULL)
	{
		pCenterUnit = pPlot->getDebugCenterUnit();

		if ((pCenterUnit != NULL) && (pCenterUnit->getOwnerINLINE() == getActivePlayer()))
		{
			pSelectUnit = pCenterUnit;
		}
	}

	if (pSelectUnit != NULL)
	{
		gDLL->getInterfaceIFace()->selectGroup(pSelectUnit, false, false, true);
	}
}


bool CvGame::selectionListIgnoreBuildingDefense() const
{
	PROFILE_FUNC();

	CLLNode<IDInfo>* pSelectedUnitNode;
	CvUnit* pSelectedUnit;
	bool bIgnoreBuilding;
	bool bAttackLandUnit;

	bIgnoreBuilding = false;
	bAttackLandUnit = false;

	pSelectedUnitNode = gDLL->getInterfaceIFace()->headSelectionListNode();

	while (pSelectedUnitNode != NULL)
	{
		pSelectedUnit = ::getUnit(pSelectedUnitNode->m_data);
		pSelectedUnitNode = gDLL->getInterfaceIFace()->nextSelectionListNode(pSelectedUnitNode);

		if (pSelectedUnit != NULL)
		{
			if (pSelectedUnit->ignoreBuildingDefense())
			{
				bIgnoreBuilding = true;
			}

			if ((pSelectedUnit->getDomainType() == DOMAIN_LAND) && pSelectedUnit->canAttack())
			{
				bAttackLandUnit = true;
			}
		}
	}

	if (!bIgnoreBuilding && !bAttackLandUnit)
	{
		if (getBestLandUnit() != NO_UNIT)
		{
			bIgnoreBuilding = GC.getUnitInfo(getBestLandUnit()).isIgnoreBuildingDefense();
		}
	}

	return bIgnoreBuilding;
}


void CvGame::implementDeal(PlayerTypes eWho, PlayerTypes eOtherWho, CLinkList<TradeData>* pOurList, CLinkList<TradeData>* pTheirList, bool bForce)
{
	CvDeal* pDeal;

	FAssertMsg(eWho != NO_PLAYER, "Who is not assigned a valid value");
	FAssertMsg(eOtherWho != NO_PLAYER, "OtherWho is not assigned a valid value");
	FAssertMsg(eWho != eOtherWho, "eWho is not expected to be equal with eOtherWho");

	pDeal = addDeal();
	pDeal->init(pDeal->getID(), eWho, eOtherWho);
	pDeal->addTrades(pOurList, pTheirList, !bForce);
	if ((pDeal->getLengthFirstTrades() == 0) && (pDeal->getLengthSecondTrades() == 0))
	{
		pDeal->kill();
	}
}


void CvGame::verifyDeals()
{
	OBSERVER_PERFORMANCE("CvGame::verifyDeals");
	CvDeal* pLoopDeal;
	int iLoop;

	for(pLoopDeal = firstDeal(&iLoop); pLoopDeal != NULL; pLoopDeal = nextDeal(&iLoop))
	{
		pLoopDeal->verify();
	}
}


/* Globeview configuration control:
If bStarsVisible, then there will be stars visible behind the globe when it is on
If bWorldIsRound, then the world will bend into a globe; otherwise, it will show up as a plane  */
void CvGame::getGlobeviewConfigurationParameters(TeamTypes eTeam, bool& bStarsVisible, bool& bWorldIsRound)
{
	if(GET_TEAM(eTeam).isMapCentering() || isCircumnavigated())
	{
		bStarsVisible = true;
		bWorldIsRound = true;
	}
	else
	{
		bStarsVisible = false;
		bWorldIsRound = false;
	}
}


int CvGame::getSymbolID(int iSymbol)
{
	return gDLL->getInterfaceIFace()->getSymbolID(iSymbol);
}


int CvGame::getAdjustedPopulationPercent(VictoryTypes eVictory) const
{
	int iPopulation;
	int iBestPopulation;
	int iNextBestPopulation;
	int iI;

	if (GC.getVictoryInfo(eVictory).getPopulationPercentLead() == 0)
	{
		return 0;
	}

	if (getTotalPopulation() == 0)
	{
		return 100;
	}

	iBestPopulation = 0;
	iNextBestPopulation = 0;

	for (iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		if (GET_TEAM((TeamTypes)iI).isAlive())
		{
			iPopulation = GET_TEAM((TeamTypes)iI).getTotalPopulation();

			if (iPopulation > iBestPopulation)
			{
				iNextBestPopulation = iBestPopulation;
				iBestPopulation = iPopulation;
			}
			else if (iPopulation > iNextBestPopulation)
			{
				iNextBestPopulation = iPopulation;
			}
		}
	}

	return std::min(100, (((iNextBestPopulation * 100) / getTotalPopulation()) + GC.getVictoryInfo(eVictory).getPopulationPercentLead()));
}


int CvGame::getProductionPerPopulation(HurryTypes eHurry)
{
	if (NO_HURRY == eHurry)
	{
		return 0;
	}
	return (GC.getHurryInfo(eHurry).getProductionPerPopulation() * 100) / std::max(1, GC.getGameSpeedInfo(getGameSpeedType()).getHurryPercent());
}


int CvGame::getAdjustedLandPercent(VictoryTypes eVictory) const
{
	int iPercent;

	if (GC.getVictoryInfo(eVictory).getLandPercent() == 0)
	{
		return 0;
	}

	iPercent = GC.getVictoryInfo(eVictory).getLandPercent();

	//Rhye
	//iPercent -= (countCivTeamsEverAlive() * 2);
	iPercent -= (countCivTeamsAlive() * 2);

	return std::max(iPercent, GC.getVictoryInfo(eVictory).getMinLandPercent());
}


bool CvGame::isTeamVote(VoteTypes eVote) const
{
	return (GC.getVoteInfo(eVote).isSecretaryGeneral() || GC.getVoteInfo(eVote).isVictory());
}


bool CvGame::isChooseElection(VoteTypes eVote) const
{
	return !(GC.getVoteInfo(eVote).isSecretaryGeneral());
}


bool CvGame::isTeamVoteEligible(TeamTypes eTeam, VoteSourceTypes eVoteSource) const
{
	CvTeam& kTeam = GET_TEAM(eTeam);

	//Rhye - start
	if (eTeam == INDEPENDENT || eTeam == INDEPENDENT2 || eTeam == NATIVE || eTeam == CELTIA)
	{
		return false;
	}
	//Rhye - end

	if (kTeam.isForceTeamVoteEligible(eVoteSource))
	{
		return true;
	}

	if (!kTeam.isFullMember(eVoteSource))
	{
		return false;
	}

	int iCount = 0;
	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		CvTeam& kLoopTeam = GET_TEAM((TeamTypes)iI);
		if (kLoopTeam.isAlive())
		{
			if (kLoopTeam.isForceTeamVoteEligible(eVoteSource))
			{
				++iCount;
			}
		}
	}

	int iExtraEligible = GC.getDefineINT("TEAM_VOTE_MIN_CANDIDATES") - iCount;
	if (iExtraEligible <= 0)
	{
		return false;
	}

	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		if (iI != eTeam)
		{
			CvTeam& kLoopTeam = GET_TEAM((TeamTypes)iI);
			if (kLoopTeam.isAlive())
			{
				if (!kLoopTeam.isForceTeamVoteEligible(eVoteSource))
				{
					if (kLoopTeam.isFullMember(eVoteSource))
					{
						int iLoopVotes = kLoopTeam.getVotes(NO_VOTE, eVoteSource);
						int iVotes = kTeam.getVotes(NO_VOTE, eVoteSource);
						if (iLoopVotes > iVotes || (iLoopVotes == iVotes && iI < eTeam))
						{
							iExtraEligible--;
						}
					}
				}
			}
		}
	}

	return (iExtraEligible > 0);
}


int CvGame::countVote(const VoteTriggeredData& kData, PlayerVoteTypes eChoice) const
{
	if (isApostolicCouncil(kData.eVoteSource)) return getCouncilTally(kData.getID(), eChoice == PLAYER_VOTE_YES ? 0 : (eChoice == PLAYER_VOTE_NO ? 2 : 1), false);
	int iCount = 0;
	//for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++) //Rhye
	for (int iI = 0; iI < NUM_MAJOR_PLAYERS; iI++) //Rhye
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			if (getPlayerVote(((PlayerTypes)iI), kData.getID()) == eChoice)
			{
				iCount += GET_PLAYER((PlayerTypes)iI).getVotes(kData.kVoteOption.eVote, kData.eVoteSource);
			}
		}
	}

	return iCount;
}


int CvGame::countPossibleVote(VoteTypes eVote, VoteSourceTypes eVoteSource) const
{
	if (isApostolicCouncil(eVoteSource) && getCouncilVoteId() >= 0) return getCouncilTally(getCouncilVoteId(), 4, false);
	int iCount;
	int iI;

	iCount = 0;

	//for (iI = 0; iI < MAX_CIV_PLAYERS; iI++) //Rhye
	for (iI = 0; iI < (isApostolicCouncil(eVoteSource) ? MAX_CIV_PLAYERS : NUM_MAJOR_PLAYERS); iI++)
	{
		iCount += GET_PLAYER((PlayerTypes)iI).getVotes(eVote, eVoteSource);
	}

	return iCount;
}



TeamTypes CvGame::findHighestVoteTeam(const VoteTriggeredData& kData) const
{
	TeamTypes eBestTeam = NO_TEAM;
	int iBestCount = 0;

	if (isTeamVote(kData.kVoteOption.eVote))
	{
		//for (int iI = 0; iI < MAX_CIV_TEAMS; ++iI) //Rhye
		for (int iI = 0; iI < NUM_MAJOR_PLAYERS; ++iI) //Rhye
		{
			if (GET_TEAM((TeamTypes)iI).isAlive())
			{
				int iCount = countVote(kData, (PlayerVoteTypes)iI);

				if (iCount > iBestCount)
				{
					iBestCount = iCount;
					eBestTeam = (TeamTypes)iI;
				}
			}
		}
	}

	return eBestTeam;
}


int CvGame::getVoteRequired(VoteTypes eVote, VoteSourceTypes eVoteSource) const
{
	if (isApostolicCouncil(eVoteSource))
	{
		int iTotal = countPossibleVote(eVote, eVoteSource);
		int iRule = GC.getVoteInfo(eVote).getPopulationThreshold();
		return iRule == 67 ? (2 * iTotal + 2) / 3 : (iRule == 0 ? 1 : iTotal / 2 + 1);
	}
	return ((countPossibleVote(eVote, eVoteSource) * GC.getVoteInfo(eVote).getPopulationThreshold()) / 100);
}


TeamTypes CvGame::getSecretaryGeneral(VoteSourceTypes eVoteSource) const
{
	if (isApostolicCouncil(eVoteSource))
	{
		CvCity* pPalace = getApostolicPalace();
		return isCouncilActive() && pPalace ? GET_PLAYER(pPalace->getOwnerINLINE()).getTeam() : NO_TEAM;
	}
	int iI;

	if (!canHaveSecretaryGeneral(eVoteSource))
	{
		for (int iBuilding = 0; iBuilding < GC.getNumBuildingInfos(); ++iBuilding)
		{
			if (GC.getBuildingInfo((BuildingTypes)iBuilding).getVoteSourceType() == eVoteSource)
			{
				//for (iI = 0; iI < MAX_CIV_PLAYERS; iI++) //Rhye
				for (iI = 0; iI < NUM_MAJOR_PLAYERS; iI++) //Rhye
				{
					CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iI);
					if (kLoopPlayer.isAlive())
					{
						if (kLoopPlayer.getBuildingClassCount((BuildingClassTypes)GC.getBuildingInfo((BuildingTypes)iBuilding).getBuildingClassType()) > 0)
						{
							ReligionTypes eReligion = getVoteSourceReligion(eVoteSource);
							if (NO_RELIGION == eReligion || kLoopPlayer.getStateReligion() == eReligion)
							{
								return kLoopPlayer.getTeam();
							}
						}
					}
				}
			}
		}
	}
	else
	{
		for (iI = 0; iI < GC.getNumVoteInfos(); iI++)
		{
			if (GC.getVoteInfo((VoteTypes)iI).isVoteSourceType(eVoteSource))
			{
				if (GC.getVoteInfo((VoteTypes)iI).isSecretaryGeneral())
				{
					if (isVotePassed((VoteTypes)iI))
					{
						return ((TeamTypes)(getVoteOutcome((VoteTypes)iI)));
					}
				}
			}
		}
	}


	return NO_TEAM;
}

bool CvGame::canHaveSecretaryGeneral(VoteSourceTypes eVoteSource) const
{
	for (int iI = 0; iI < GC.getNumVoteInfos(); iI++)
	{
		if (GC.getVoteInfo((VoteTypes)iI).isVoteSourceType(eVoteSource))
		{
			if (GC.getVoteInfo((VoteTypes)iI).isSecretaryGeneral())
			{
				return true;
			}
		}
	}

	return false;
}

void CvGame::clearSecretaryGeneral(VoteSourceTypes eVoteSource)
{
	for (int j = 0; j < GC.getNumVoteInfos(); ++j)
	{
		CvVoteInfo& kVote = GC.getVoteInfo((VoteTypes)j);

		if (kVote.isVoteSourceType(eVoteSource))
		{
			if (kVote.isSecretaryGeneral())
			{
				VoteTriggeredData kData;
				kData.eVoteSource = eVoteSource;
				kData.kVoteOption.eVote = (VoteTypes)j;
				kData.kVoteOption.iCityId = -1;
				kData.kVoteOption.szText.empty();
				kData.kVoteOption.ePlayer = NO_PLAYER;
				setVoteOutcome(kData, NO_PLAYER_VOTE);
				setSecretaryGeneralTimer(eVoteSource, 0);
			}
		}
	}
}

void CvGame::updateSecretaryGeneral()
{
	for (int i = 0; i < GC.getNumVoteSourceInfos(); ++i)
	{
		TeamTypes eSecretaryGeneral = getSecretaryGeneral((VoteSourceTypes)i);
		if (NO_TEAM != eSecretaryGeneral && !GET_TEAM(eSecretaryGeneral).isFullMember((VoteSourceTypes)i))
		{
			clearSecretaryGeneral((VoteSourceTypes)i);
		}
	}
}

int CvGame::countCivPlayersAlive() const
{
	int iCount = 0;

	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			iCount++;
		}
	}

	return iCount;
}


int CvGame::countCivPlayersEverAlive() const
{
	int iCount = 0;

	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes) iI);
		if (kPlayer.isEverAlive())
		{
			if (kPlayer.getParent() == NO_PLAYER)
			{
				iCount++;
			}
		}
	}

	return iCount;
}


int CvGame::countCivTeamsAlive() const
{
	int iCount = 0;

	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		if (GET_TEAM((TeamTypes)iI).isAlive())
		{
			iCount++;
		}
	}

	return iCount;
}


int CvGame::countCivTeamsEverAlive() const
{
	std::set<int> setTeamsEverAlive;

	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes) iI);
		if (kPlayer.isEverAlive())
		{
			if (kPlayer.getParent() == NO_PLAYER)
			{
				setTeamsEverAlive.insert(kPlayer.getTeam());
			}
		}
	}

	return setTeamsEverAlive.size();
}


int CvGame::countHumanPlayersAlive() const
{
	int iCount = 0;

	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes) iI);
		if (kPlayer.isAlive() && kPlayer.isHuman())
		{
			iCount++;
		}
	}

	return iCount;
}


int CvGame::countTotalCivPower()
{
	int iCount = 0;

	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes) iI);
		if (kPlayer.isAlive())
		{
			iCount += kPlayer.getPower();
		}
	}

	return iCount;
}


int CvGame::countTotalNukeUnits()
{
	int iCount = 0;
	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes) iI);
		if (kPlayer.isAlive())
		{
			iCount += kPlayer.getNumNukeUnits();
		}
	}

	return iCount;
}


int CvGame::countKnownTechNumTeams(TechTypes eTech)
{
	int iCount = 0;

	for (int iI = 0; iI < MAX_TEAMS; iI++)
	{
		if (GET_TEAM((TeamTypes)iI).isEverAlive())
		{
			if (GET_TEAM((TeamTypes)iI).isHasTech(eTech))
			{
				iCount++;
			}
		}
	}

	return iCount;
}


int CvGame::getNumFreeBonuses(BuildingTypes eBuilding)
{
	if (GC.getBuildingInfo(eBuilding).getNumFreeBonuses() == -1)
	{
		return GC.getWorldInfo(GC.getMapINLINE().getWorldSize()).getNumFreeBuildingBonuses();
	}
	else
	{
		return GC.getBuildingInfo(eBuilding).getNumFreeBonuses();
	}
}


int CvGame::getShrinePopulationCommerce(ReligionTypes eReligion)
{
    if (eReligion == NO_RELIGION) return 0;
    if (m_bShrinePopulationDirty || (int)m_aiShrinePopulationCommerce.size() != GC.getNumReligionInfos())
    {
        // Exact shares for every possible religion count: LCM(1..7) = 420.
        // Sum before dividing by five, so small mixed cities are not rounded away.
        int iScale = 1;
        for (int n = 2; n <= GC.getNumReligionInfos(); ++n)
        {
            int a = iScale, b = n;
            while (b != 0) { const int r = a % b; a = b; b = r; }
            iScale = iScale / a * n;
        }
        std::vector<__int64> aiPopulation(GC.getNumReligionInfos(), 0);
        for (int iPlayer = 0; iPlayer < MAX_PLAYERS; ++iPlayer)
        {
            int iLoop;
            for (CvCity* pCity = GET_PLAYER((PlayerTypes)iPlayer).firstCity(&iLoop); pCity != NULL;
                 pCity = GET_PLAYER((PlayerTypes)iPlayer).nextCity(&iLoop))
            {
                const int iReligions = pCity->getReligionCount();
                if (iReligions == 0) continue;
                const __int64 iShare = (__int64)pCity->getPopulation() * (iScale / iReligions);
                for (int iReligion = 0; iReligion < GC.getNumReligionInfos(); ++iReligion)
                    if (pCity->isHasReligion((ReligionTypes)iReligion)) aiPopulation[iReligion] += iShare;
            }
        }
        m_aiShrinePopulationCommerce.assign(GC.getNumReligionInfos(), 0);
        for (int iReligion = 0; iReligion < GC.getNumReligionInfos(); ++iReligion)
            m_aiShrinePopulationCommerce[iReligion] = (int)(aiPopulation[iReligion] / ((__int64)iScale * 5));
        m_bShrinePopulationDirty = false;
    }
    return m_aiShrinePopulationCommerce[eReligion];
}

void CvGame::updateShrineCommerce()
{
    if (getShrineBuildingCount() == 0) return;
    for (int iPlayer = 0; iPlayer < MAX_PLAYERS; ++iPlayer)
    {
        int iLoop;
        for (CvCity* pCity = GET_PLAYER((PlayerTypes)iPlayer).firstCity(&iLoop); pCity != NULL;
             pCity = GET_PLAYER((PlayerTypes)iPlayer).nextCity(&iLoop)) pCity->updateShrineCommerce();
    }
}

int CvGame::countReligionLevels(ReligionTypes eReligion)
{
	int iCount;
	int iI;

	iCount = 0;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			iCount += GET_PLAYER((PlayerTypes)iI).getHasReligionCount(eReligion);
		}
	}

	return iCount;
}

int CvGame::countCorporationLevels(CorporationTypes eCorporation)
{
	int iCount = 0;

	for (int iI = 0; iI < MAX_PLAYERS; iI++)
	{
		CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iI);
		if (kLoopPlayer.isAlive())
		{
			iCount += GET_PLAYER((PlayerTypes)iI).getHasCorporationCount(eCorporation);
		}
	}

	return iCount;
}

void CvGame::replaceCorporation(CorporationTypes eCorporation1, CorporationTypes eCorporation2)
{
	for (int iI = 0; iI < MAX_PLAYERS; iI++)
	{
		CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iI);
		if (kLoopPlayer.isAlive())
		{
			int iIter;
			for (CvCity* pCity = kLoopPlayer.firstCity(&iIter); NULL != pCity; pCity = kLoopPlayer.nextCity(&iIter))
			{
				if (pCity->isHasCorporation(eCorporation1))
				{
					pCity->setHasCorporation(eCorporation1, false, false, false);
					pCity->setHasCorporation(eCorporation2, true, true);
				}
			}

			for (CvUnit* pUnit = kLoopPlayer.firstUnit(&iIter); NULL != pUnit; pUnit = kLoopPlayer.nextUnit(&iIter))
			{
				if (pUnit->getUnitInfo().getCorporationSpreads(eCorporation1) > 0)
				{
					pUnit->kill(false);
				}
			}
		}
	}
}


int CvGame::calculateReligionPercent(ReligionTypes eReligion) const
{
	CvCity* pLoopCity;
	int iCount;
	int iLoop;
	int iI;

	if (getTotalPopulation() == 0)
	{
		return 0;
	}

	iCount = 0;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			for (pLoopCity = GET_PLAYER((PlayerTypes)iI).firstCity(&iLoop); pLoopCity != NULL; pLoopCity = GET_PLAYER((PlayerTypes)iI).nextCity(&iLoop))
			{
				if (pLoopCity->isHasReligion(eReligion))
				{
					iCount += ((pLoopCity->getPopulation() + (pLoopCity->getReligionCount() / 2)) / pLoopCity->getReligionCount());
				}
			}
		}
	}

	return ((iCount * 100) / getTotalPopulation());
}


int CvGame::goldenAgeLength() const
{
	int iLength;

	iLength = GC.getDefineINT("GOLDEN_AGE_LENGTH");

	iLength *= GC.getGameSpeedInfo(getGameSpeedType()).getGoldenAgePercent();
	iLength /= 100;

	return iLength;
}

int CvGame::victoryDelay(VictoryTypes eVictory) const
{
	FAssert(eVictory >= 0 && eVictory < GC.getNumVictoryInfos());

	int iLength = GC.getVictoryInfo(eVictory).getVictoryDelayTurns();

	iLength *= GC.getGameSpeedInfo(getGameSpeedType()).getVictoryDelayPercent();
	iLength /= 100;

	return iLength;
}



int CvGame::getImprovementUpgradeTime(ImprovementTypes eImprovement) const
{
	int iTime;

	iTime = GC.getImprovementInfo(eImprovement).getUpgradeTime();

	iTime *= GC.getGameSpeedInfo(getGameSpeedType()).getImprovementPercent();
	iTime /= 100;

	iTime *= GC.getEraInfo(getStartEra()).getImprovementPercent();
	iTime /= 100;

	return iTime;
}


bool CvGame::canTrainNukes() const
{
	for (int iI = 0; iI < MAX_PLAYERS; iI++)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)iI);
		if (kPlayer.isAlive())
		{
			for (int iJ = 0; iJ < GC.getNumUnitClassInfos(); iJ++)
			{
				UnitTypes eUnit = (UnitTypes)GC.getCivilizationInfo(kPlayer.getCivilizationType()).getCivilizationUnits((UnitClassTypes)iJ);

				if (NO_UNIT != eUnit)
				{
					if (-1 != GC.getUnitInfo(eUnit).getNukeRange())
					{
						if (kPlayer.canTrain(eUnit))
						{
							return true;
						}
					}
				}
			}
		}
	}

	return false;
}


EraTypes CvGame::getCurrentEra() const
{
	int iEra;
	int iCount;
	int iI;

	iEra = 0;
	iCount = 0;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			iEra += GET_PLAYER((PlayerTypes)iI).getCurrentEra();
			iCount++;
		}
	}

	if (iCount > 0)
	{
		return ((EraTypes)(iEra / iCount));
	}

	return NO_ERA;
}


TeamTypes CvGame::getActiveTeam() const
{
	if (getActivePlayer() == NO_PLAYER)
	{
		return NO_TEAM;	
	}
	else
	{
		return (TeamTypes)GET_PLAYER(getActivePlayer()).getTeam();
	}
}


CivilizationTypes CvGame::getActiveCivilizationType() const
{
	if (getActivePlayer() == NO_PLAYER)
	{
		return NO_CIVILIZATION;
	}
	else
	{
		return (CivilizationTypes)GET_PLAYER(getActivePlayer()).getCivilizationType();
	}
}


bool CvGame::isNetworkMultiPlayer() const																	 
{
	return GC.getInitCore().getMultiplayer();
}


bool CvGame::isGameMultiPlayer() const																 
{
	return (isNetworkMultiPlayer() || isPbem() || isHotSeat());
}


bool CvGame::isTeamGame() const																		 
{
	FAssert(countCivPlayersAlive() >= countCivTeamsAlive());
	return (countCivPlayersAlive() > countCivTeamsAlive());
}


bool CvGame::isModem()
{
	return gDLL->IsModem();
}
void CvGame::setModem(bool bModem)
{
	if (bModem)
	{
		gDLL->ChangeINIKeyValue("CONFIG", "Bandwidth", "modem");
	}
	else
	{
		gDLL->ChangeINIKeyValue("CONFIG", "Bandwidth", "broadband");
	}

	gDLL->SetModem(bModem);
}


void CvGame::reviveActivePlayer()
{
	if (!(GET_PLAYER(getActivePlayer()).isAlive()))
	{
		setAIAutoPlay(0);

		GC.getInitCore().setSlotStatus(getActivePlayer(), SS_TAKEN);
		
		// Let Python handle it
		//Rhye - start
//Speed: Modified by Kael 04/19/2007
//		long lResult=0;
//		CyArgsList argsList;
//		argsList.add(getActivePlayer());
//
//		gDLL->getPythonIFace()->callFunction(PYGameModule, "doReviveActivePlayer", argsList.makeFunctionArgs(), &lResult);
//		if (lResult == 1)
//		{
//			return;
//		}
//Speed: End Modify
		//Rhye - end

		//GET_PLAYER(getActivePlayer()).initUnit(((UnitTypes)0), 0, 0); //Rhye
		GET_PLAYER(getActivePlayer()).initUnit(((UnitTypes)82), 0, 0); //Rhye (catapult)
		//logMsg("init catapult in 00"); //Rhye
	}
}


int CvGame::getNumHumanPlayers()
{
	return GC.getInitCore().getNumHumans();
}

int CvGame::getGameTurn()
{
	return GC.getInitCore().getGameTurn();
}


void CvGame::setGameTurn(int iNewValue)
{
	if (getGameTurn() != iNewValue)
	{
		GC.getInitCore().setGameTurn(iNewValue);
		FAssert(getGameTurn() >= 0);

		updateBuildingCommerce();

		setScoreDirty(true);

		gDLL->getInterfaceIFace()->setDirty(TurnTimer_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(GameData_DIRTY_BIT, true);
	}
}


void CvGame::incrementGameTurn()
{
	setGameTurn(getGameTurn() + 1);
}


int CvGame::getTurnYear(int iGameTurn)
{
	// The 1453 start uses the 1450 turn slot, followed by the normal 1455 turn.
	// This keeps all later RFC birth/deadline turns on the original calendar.
	if (getStartTurn() == 271 && getStartYear() == -3000 && iGameTurn == 271)
		return 1453;
	// moved the body of this method to Game Core Utils so we have access for other games than the current one (replay screen in HOF)
	return getTurnYearForGame(iGameTurn, getStartYear(), getCalendar(), getGameSpeedType());
}


int CvGame::getGameTurnYear()
{
	return getTurnYear(getGameTurn());
}


int CvGame::getElapsedGameTurns() const
{
	return m_iElapsedGameTurns;
}


void CvGame::incrementElapsedGameTurns()
{
	m_iElapsedGameTurns++;
}


int CvGame::getMaxTurns() const
{
	return GC.getInitCore().getMaxTurns();
}


void CvGame::setMaxTurns(int iNewValue)
{
	GC.getInitCore().setMaxTurns(iNewValue);
	FAssert(getMaxTurns() >= 0);
}


void CvGame::changeMaxTurns(int iChange)
{
	setMaxTurns(getMaxTurns() + iChange);
}


int CvGame::getMaxCityElimination() const
{
	return GC.getInitCore().getMaxCityElimination();
}


void CvGame::setMaxCityElimination(int iNewValue)
{
	GC.getInitCore().setMaxCityElimination(iNewValue);
	FAssert(getMaxCityElimination() >= 0);
}

int CvGame::getNumAdvancedStartPoints() const
{
	return GC.getInitCore().getNumAdvancedStartPoints();
}


void CvGame::setNumAdvancedStartPoints(int iNewValue)
{
	GC.getInitCore().setNumAdvancedStartPoints(iNewValue);
	FAssert(getNumAdvancedStartPoints() >= 0);
}

int CvGame::getStartTurn() const
{
	return m_iStartTurn;
}


void CvGame::setStartTurn(int iNewValue)
{
	m_iStartTurn = iNewValue;
}


int CvGame::getStartYear() const
{
	return m_iStartYear;
}


void CvGame::setStartYear(int iNewValue)
{
	m_iStartYear = iNewValue;
}


int CvGame::getEstimateEndTurn() const
{
	return m_iEstimateEndTurn;
}


void CvGame::setEstimateEndTurn(int iNewValue)
{
	m_iEstimateEndTurn = iNewValue;
}


int CvGame::getTurnSlice() const
{
	return m_iTurnSlice;
}


int CvGame::getMinutesPlayed() const
{
	return (getTurnSlice() / gDLL->getTurnsPerMinute());
}


void CvGame::setTurnSlice(int iNewValue)
{
	m_iTurnSlice = iNewValue;
}


void CvGame::changeTurnSlice(int iChange)
{
	setTurnSlice(getTurnSlice() + iChange);
}


int CvGame::getCutoffSlice() const
{
	return m_iCutoffSlice;
}


void CvGame::setCutoffSlice(int iNewValue)
{
	m_iCutoffSlice = iNewValue;
}


void CvGame::changeCutoffSlice(int iChange)
{
	setCutoffSlice(getCutoffSlice() + iChange);
}


int CvGame::getTurnSlicesRemaining()
{
	return (getCutoffSlice() - getTurnSlice());
}


void CvGame::resetTurnTimer()
{
	// We should only use the turn timer if we are in multiplayer
	if (isMPOption(MPOPTION_TURN_TIMER))
	{
		if (getElapsedGameTurns() > 0 || !isOption(GAMEOPTION_ADVANCED_START))
		{
			// Determine how much time we should allow
			int iTurnLen = getMaxTurnLen();
			if (getElapsedGameTurns() == 0 && !isPitboss())
			{
				// Let's allow more time for the initial turn
				TurnTimerTypes eTurnTimer = GC.getInitCore().getTurnTimer();
				FAssertMsg(eTurnTimer >= 0 && eTurnTimer < GC.getNumTurnTimerInfos(), "Invalid TurnTimer selection in InitCore");
				iTurnLen = (iTurnLen * GC.getTurnTimerInfo(eTurnTimer).getFirstTurnMultiplier());
			}
			// Set the current turn slice to start the 'timer'
			setCutoffSlice(getTurnSlice() + iTurnLen);
		}
	}
}

void CvGame::incrementTurnTimer(int iNumTurnSlices)
{
	if (isMPOption(MPOPTION_TURN_TIMER))
	{
		// If the turn timer has expired, we shouldn't increment it as we've sent our turn complete message
		if (getTurnSlice() <= getCutoffSlice())
		{
			changeCutoffSlice(iNumTurnSlices);
		}
	}
}


int CvGame::getMaxTurnLen()
{
	if (isPitboss())
	{
		// Use the user provided input
		// Turn time is in hours
		return ( getPitbossTurnTime() * 3600 * 4);
	}
	else
	{
		int iMaxUnits = 0;
		int iMaxCities = 0;

		// Find out who has the most units and who has the most cities
		// Calculate the max turn time based on the max number of units and cities
		for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
		{
			if (GET_PLAYER((PlayerTypes)i).isAlive())
			{
				if (GET_PLAYER((PlayerTypes)i).getNumUnits() > iMaxUnits)
				{
					iMaxUnits = GET_PLAYER((PlayerTypes)i).getNumUnits();
				}
				if (GET_PLAYER((PlayerTypes)i).getNumCities() > iMaxCities)
				{
					iMaxCities = GET_PLAYER((PlayerTypes)i).getNumCities();
				}
			}
		}

		// Now return turn len based on base len and unit and city bonuses
		TurnTimerTypes eTurnTimer = GC.getInitCore().getTurnTimer();
		FAssertMsg(eTurnTimer >= 0 && eTurnTimer < GC.getNumTurnTimerInfos(), "Invalid TurnTimer Selection in InitCore");
		return ( GC.getTurnTimerInfo(eTurnTimer).getBaseTime() + 
			    (GC.getTurnTimerInfo(eTurnTimer).getCityBonus()*iMaxCities) +
				(GC.getTurnTimerInfo(eTurnTimer).getUnitBonus()*iMaxUnits) );
	}
}


int CvGame::getTargetScore() const
{
	return GC.getInitCore().getTargetScore();
}


void CvGame::setTargetScore(int iNewValue)
{
	GC.getInitCore().setTargetScore(iNewValue);
	FAssert(getTargetScore() >= 0);
}


int CvGame::getNumGameTurnActive()
{
	return m_iNumGameTurnActive;
}


int CvGame::countNumHumanGameTurnActive() const
{
	int iCount;
	int iI;

	iCount = 0;

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isHuman())
		{
			if (GET_PLAYER((PlayerTypes)iI).isTurnActive())
			{
				iCount++;
			}
		}
	}

	return iCount;
}


void CvGame::changeNumGameTurnActive(int iChange)
{
	m_iNumGameTurnActive = (m_iNumGameTurnActive + iChange);
	FAssert(getNumGameTurnActive() >= 0);
}


int CvGame::getNumCities() const																		
{
	return m_iNumCities;
}


int CvGame::getNumCivCities() const
{
	return (getNumCities() - GET_PLAYER(BARBARIAN_PLAYER).getNumCities());
}


void CvGame::changeNumCities(int iChange)
{
	m_iNumCities = (m_iNumCities + iChange);
	FAssert(getNumCities() >= 0);
}


int CvGame::getTotalPopulation() const
{
	return m_iTotalPopulation;
}


void CvGame::changeTotalPopulation(int iChange)
{
	m_iTotalPopulation = (m_iTotalPopulation + iChange);
	FAssert(getTotalPopulation() >= 0);
}


int CvGame::getTradeRoutes() const
{
	return m_iTradeRoutes;
}


void CvGame::changeTradeRoutes(int iChange)
{
	if (iChange != 0)
	{
		m_iTradeRoutes = (m_iTradeRoutes + iChange);
		FAssert(getTradeRoutes() >= 0);

		updateTradeRoutes();
	}
}


int CvGame::getFreeTradeCount() const
{
	return m_iFreeTradeCount;
}


bool CvGame::isFreeTrade() const
{
	return (getFreeTradeCount() > 0);
}


void CvGame::changeFreeTradeCount(int iChange)
{
	bool bOldFreeTrade;

	if (iChange != 0)
	{
		bOldFreeTrade = isFreeTrade();

		m_iFreeTradeCount = (m_iFreeTradeCount + iChange);
		FAssert(getFreeTradeCount() >= 0);

		if (bOldFreeTrade != isFreeTrade())
		{
			updateTradeRoutes();
		}
	}
}


int CvGame::getNoNukesCount() const
{
	return m_iNoNukesCount;
}


bool CvGame::isNoNukes() const
{
	return (getNoNukesCount() > 0);
}


void CvGame::changeNoNukesCount(int iChange)
{
	m_iNoNukesCount = (m_iNoNukesCount + iChange);
	FAssert(getNoNukesCount() >= 0);
}


int CvGame::getSecretaryGeneralTimer(VoteSourceTypes eVoteSource) const
{
	FAssert(eVoteSource >= 0);
	FAssert(eVoteSource < GC.getNumVoteSourceInfos());
	return m_aiSecretaryGeneralTimer[eVoteSource];
}


void CvGame::setSecretaryGeneralTimer(VoteSourceTypes eVoteSource, int iNewValue)
{
	FAssert(eVoteSource >= 0);
	FAssert(eVoteSource < GC.getNumVoteSourceInfos());
	m_aiSecretaryGeneralTimer[eVoteSource] = iNewValue;
	FAssert(getSecretaryGeneralTimer(eVoteSource) >= 0);
}


void CvGame::changeSecretaryGeneralTimer(VoteSourceTypes eVoteSource, int iChange)
{
	setSecretaryGeneralTimer(eVoteSource, getSecretaryGeneralTimer(eVoteSource) + iChange);
}


int CvGame::getVoteTimer(VoteSourceTypes eVoteSource) const
{
	FAssert(eVoteSource >= 0);
	FAssert(eVoteSource < GC.getNumVoteSourceInfos());
	return m_aiVoteTimer[eVoteSource];
}


void CvGame::setVoteTimer(VoteSourceTypes eVoteSource, int iNewValue)
{
	FAssert(eVoteSource >= 0);
	FAssert(eVoteSource < GC.getNumVoteSourceInfos());
	m_aiVoteTimer[eVoteSource] = iNewValue;
	FAssert(getVoteTimer(eVoteSource) >= 0);
}


void CvGame::changeVoteTimer(VoteSourceTypes eVoteSource, int iChange)
{
	setVoteTimer(eVoteSource, getVoteTimer(eVoteSource) + iChange);
}


int CvGame::getNukesExploded() const
{
	return m_iNukesExploded;
}


void CvGame::changeNukesExploded(int iChange)
{
	m_iNukesExploded = (m_iNukesExploded + iChange);
}


int CvGame::getMaxPopulation() const
{
	return m_iMaxPopulation;
}


int CvGame::getMaxLand() const
{
	return m_iMaxLand;
}


int CvGame::getMaxTech() const
{
	return m_iMaxTech;
}


int CvGame::getMaxWonders() const
{
	return m_iMaxWonders;
}


int CvGame::getInitPopulation() const
{
	return m_iInitPopulation;
}


int CvGame::getInitLand() const
{
	return m_iInitLand;
}


int CvGame::getInitTech() const
{
	return m_iInitTech;
}


int CvGame::getInitWonders() const
{
	return m_iInitWonders;
}


void CvGame::initScoreCalculation()
{
	// initialize score calculation
	int iMaxFood = 0;
	for (int i = 0; i < GC.getMapINLINE().numPlotsINLINE(); i++)
	{
		CvPlot* pPlot = GC.getMapINLINE().plotByIndexINLINE(i);
		if (!pPlot->isWater() || pPlot->isAdjacentToLand())
		{
			iMaxFood += pPlot->calculateBestNatureYield(YIELD_FOOD, NO_TEAM);
		}
	}
	m_iMaxPopulation = getPopulationScore(iMaxFood / std::max(1, GC.getFOOD_CONSUMPTION_PER_POPULATION()));
	m_iMaxLand = getLandPlotsScore(GC.getMapINLINE().getLandPlots());
	m_iMaxTech = 0;
	for (int i = 0; i < GC.getNumTechInfos(); i++)
	{
		m_iMaxTech += getTechScore((TechTypes)i);
	}
	m_iMaxWonders = 0;
	for (int i = 0; i < GC.getNumBuildingClassInfos(); i++)
	{
		m_iMaxWonders += getWonderScore((BuildingClassTypes)i);
	}

	if (NO_ERA != getStartEra())
	{
		int iNumSettlers = GC.getEraInfo(getStartEra()).getStartingUnitMultiplier();
		m_iInitPopulation = getPopulationScore(iNumSettlers * (GC.getEraInfo(getStartEra()).getFreePopulation() + 1));
		m_iInitLand = getLandPlotsScore(iNumSettlers *  NUM_CITY_PLOTS);
	}
	else
	{
		m_iInitPopulation = 0;
		m_iInitLand = 0;
	}

	m_iInitTech = 0;
	for (int i = 0; i < GC.getNumTechInfos(); i++)
	{
		if (GC.getTechInfo((TechTypes)i).getEra() < getStartEra())
		{
			m_iInitTech += getTechScore((TechTypes)i);
		}
		else
		{
			// count all possible free techs as initial to lower the score from immediate retirement
			for (int iCiv = 0; iCiv < GC.getNumCivilizationInfos(); iCiv++)
			{
				if (GC.getCivilizationInfo((CivilizationTypes)iCiv).isPlayable())
				{
					if (GC.getCivilizationInfo((CivilizationTypes)iCiv).isCivilizationFreeTechs(i))
					{
						m_iInitTech += getTechScore((TechTypes)i);
						break;
					}
				}
			}
		}
	}
	m_iInitWonders = 0;
}


int CvGame::getAIAutoPlay()
{
	return m_iAIAutoPlay;
}


#if ARFC_ENABLE_REPORTING
void CvGame::setObserverAutoPlay(bool enabled)
{
	// Preserve every civilization and its units. Never enable in multiplayer.
	if (isGameMultiPlayer() || m_bObserverAutoPlay == enabled) return;
	if (!enabled) setObserverRevealMap(false);
	m_bObserverAutoPlay = enabled;
	// Keep suppression through the final turn after observer AI is disabled.
	// Transient session state: reset for new games, never serialized in saves.
	if (enabled) m_bObserverNoAutosaves = true;
	if (enabled) observerPerformanceStart();
	else {
		observerPerformanceFlush();
		g_observerPerformance = false;
	}
	// AI simulations render only a progress screen; no spectator reveal or
	// forced world-graphics refresh is needed.
	gDLL->getInterfaceIFace()->setDirty(GameData_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(Score_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(MinimapSection_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(UnitInfo_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(CityInfo_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(GlobeLayer_DIRTY_BIT, true);
	gDLL->getEngineIFace()->SetDirty(MinimapTexture_DIRTY_BIT, true);
	gDLL->getEngineIFace()->SetDirty(CultureBorders_DIRTY_BIT, true);
}
#endif

#if ARFC_ENABLE_REPORTING
void CvGame::setObserverRevealMap(bool enabled)
{
	if (isGameMultiPlayer() || (enabled && !isObserverAutoPlay()) || m_bObserverRevealMap == enabled) return;
	m_bObserverRevealMap = enabled;
	if (enabled) gDLL->getEngineIFace()->PushFogOfWar(FOGOFWARMODE_OFF);
	else gDLL->getEngineIFace()->PopFogOfWar();
	gDLL->getEngineIFace()->setFogOfWarFromStack();
	GC.getMapINLINE().updateVisibility();
	GC.getMapINLINE().updateSymbols();
	GC.getMapINLINE().updateMinimapColor();
	gDLL->getInterfaceIFace()->setDirty(GlobeLayer_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(Score_DIRTY_BIT, true);
	gDLL->getEngineIFace()->SetDirty(MinimapTexture_DIRTY_BIT, true);
	gDLL->getEngineIFace()->SetDirty(CultureBorders_DIRTY_BIT, true);
}
#endif

void CvGame::setAIAutoPlay(int iNewValue)
{
	int iOldValue;

	iOldValue = getAIAutoPlay();

	if (iOldValue != iNewValue)
	{
		m_iAIAutoPlay = std::max(0, iNewValue);

		if ((iOldValue == 0) && (getAIAutoPlay() > 0))
		{
			GET_PLAYER(getActivePlayer()).killUnits();
			GET_PLAYER(getActivePlayer()).killCities();
		}
	}
}

//Rhye - start
void CvGame::setAIAutoPlayCatapult(int iNewValue)
{
	int iOldValue;

	iOldValue = getAIAutoPlay();

	if (iOldValue != iNewValue)
	{
		m_iAIAutoPlay = std::max(0, iNewValue);

		if ((iOldValue == 0) && (getAIAutoPlay() > 0))
		{
			CvPlot* pPlot = GC.getMapINLINE().plotINLINE(0, 0);
			if (pPlot->isUnit()) {
				GC.getMapINLINE().plotINLINE(0, 0)->getUnitByIndex(0)->kill(false);
				for (int iI = 0; iI < MAX_PLAYERS; iI++)
				{
					if (GET_PLAYER((PlayerTypes)iI).isHuman())
					{
						GC.getMapINLINE().plotINLINE(0, 0)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(0, 1)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(1, 0)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(1, 1)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(123, 0)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(123, 1)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(2, 0)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(2, 1)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(2, 2)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(1, 2)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(0, 2)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(123, 2)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(122, 2)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(122, 1)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
						GC.getMapINLINE().plotINLINE(122, 0)->setRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false, NO_TEAM, true);
					}
				}		
			}
			else {
				logMsg("NO UNIT IN 0,0!!!"); //Rhye
			}
		}
	}
}
//Rhye - end


void CvGame::changeAIAutoPlay(int iChange)
{
	setAIAutoPlay(getAIAutoPlay() + iChange);
}


unsigned int CvGame::getInitialTime()
{
	return m_uiInitialTime;
}


void CvGame::setInitialTime(unsigned int uiNewValue)
{
	m_uiInitialTime = uiNewValue;
}


bool CvGame::isScoreDirty() const
{
	return m_bScoreDirty;
}


void CvGame::setScoreDirty(bool bNewValue)
{
	m_bScoreDirty = bNewValue;
}


bool CvGame::isCircumnavigated() const
{
	return m_bCircumnavigated;
}


void CvGame::makeCircumnavigated()
{
	m_bCircumnavigated = true;
}

//Rhye - start
int CvGame::getCircumnavigated()
{
	return m_iCircumnavigated;
}


void CvGame::setCircumnavigated(int i)
{
	m_iCircumnavigated = i;
}
//Rhye - end

bool CvGame::circumnavigationAvailable() const
{
	if (isCircumnavigated())
	{
		return false;
	}

	if (GC.getDefineINT("CIRCUMNAVIGATE_FREE_MOVES") == 0)
	{
		return false;
	}

	CvMap& kMap = GC.getMapINLINE();

	if (!(kMap.isWrapXINLINE()) && !(kMap.isWrapYINLINE()))
	{
		return false;
	}

	if (kMap.getLandPlots() > ((kMap.numPlotsINLINE() * 2) / 3))
	{
		return false;
	}

	return true;
}

bool CvGame::isDiploVote(VoteSourceTypes eVoteSource) const
{
	return (getDiploVoteCount(eVoteSource) > 0 && (!isApostolicCouncil(eVoteSource) || isCouncilActive()));
}


int CvGame::getDiploVoteCount(VoteSourceTypes eVoteSource) const
{
	FAssert(eVoteSource >= 0 && eVoteSource < GC.getNumVoteSourceInfos());
	return m_aiDiploVote[eVoteSource];
}


void CvGame::changeDiploVote(VoteSourceTypes eVoteSource, int iChange)
{
	FAssert(eVoteSource >= 0 && eVoteSource < GC.getNumVoteSourceInfos());

	if (0 != iChange)
	{
		for (int iPlayer = 0; iPlayer < MAX_PLAYERS; ++iPlayer)
		{
			GET_PLAYER((PlayerTypes)iPlayer).processVoteSourceBonus(eVoteSource, false);
		}

		m_aiDiploVote[eVoteSource] += iChange;
		FAssert(getDiploVoteCount(eVoteSource) >= 0);

		for (int iPlayer = 0; iPlayer < MAX_PLAYERS; ++iPlayer)
		{
			GET_PLAYER((PlayerTypes)iPlayer).processVoteSourceBonus(eVoteSource, true);
		}
	}
}

bool CvGame::canDoResolution(VoteSourceTypes eVoteSource, const VoteSelectionSubData& kData) const
{
	if (isApostolicCouncil(eVoteSource)) return canCouncilPropose(kData);
	if (GC.getVoteInfo(kData.eVote).isVictory())
	{
		for (int iTeam = 0; iTeam < MAX_CIV_TEAMS; ++iTeam)
		{
			CvTeam& kTeam = GET_TEAM((TeamTypes)iTeam);

			if (kTeam.isVotingMember(eVoteSource))
			{
				if (kTeam.getVotes(kData.eVote, eVoteSource) >= getVoteRequired(kData.eVote, eVoteSource))
				{
					// Can't vote on a winner if one team already has all the votes necessary to win
					return false;
				}
			}
		}
	}

	for (int iPlayer = 0; iPlayer < MAX_CIV_PLAYERS; ++iPlayer)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)iPlayer);

		if (kPlayer.isVotingMember(eVoteSource))
		{
			if (!kPlayer.canDoResolution(eVoteSource, kData))
			{
				return false;
			}
		}
		else if (kPlayer.isAlive() && !kPlayer.isBarbarian() && !kPlayer.isMinorCiv())
		{
			// all players need to be able to vote for a diplo victory
			if (GC.getVoteInfo(kData.eVote).isVictory())
			{
				return false;
			}
		}
	}

	return true;
}

bool CvGame::isValidVoteSelection(VoteSourceTypes eVoteSource, const VoteSelectionSubData& kData) const
{
	if (isApostolicCouncil(eVoteSource)) return canCouncilPropose(kData);
	if (NO_PLAYER != kData.ePlayer)
	{
		CvPlayer& kPlayer = GET_PLAYER(kData.ePlayer);
		if (!kPlayer.isAlive() || kPlayer.isBarbarian() || kPlayer.isMinorCiv())
		{
			return false;
		}
	}

	if (NO_PLAYER != kData.eOtherPlayer)
	{
		CvPlayer& kPlayer = GET_PLAYER(kData.eOtherPlayer);
		if (!kPlayer.isAlive() || kPlayer.isBarbarian() || kPlayer.isMinorCiv())
		{
			return false;
		}
	}

	int iNumVoters = 0;
	for (int iTeam = 0; iTeam < MAX_CIV_TEAMS; ++iTeam)
	{
		if (GET_TEAM((TeamTypes)iTeam).isVotingMember(eVoteSource))
		{
			++iNumVoters;
		}
	}
	if (iNumVoters  < GC.getVoteInfo(kData.eVote).getMinVoters())
	{
		return false;
	}

	if (GC.getVoteInfo(kData.eVote).isOpenBorders())
	{
		bool bOpenWithEveryone = true;
		for (int iTeam1 = 0; iTeam1 < MAX_CIV_TEAMS; ++iTeam1)
		{
			if (GET_TEAM((TeamTypes)iTeam1).isFullMember(eVoteSource))
			{
				for (int iTeam2 = iTeam1 + 1; iTeam2 < MAX_CIV_TEAMS; ++iTeam2)
				{
					CvTeam& kTeam2 = GET_TEAM((TeamTypes)iTeam2);

					if (kTeam2.isFullMember(eVoteSource))
					{
						if (!kTeam2.isOpenBorders((TeamTypes)iTeam1))
						{
							bOpenWithEveryone = false;
							break;
						}
					}
				}
			}
		}
		if (bOpenWithEveryone)
		{
			return false;
		}
	}
	else if (GC.getVoteInfo(kData.eVote).isDefensivePact())
	{
		bool bPactWithEveryone = true;
		for (int iTeam1 = 0; iTeam1 < MAX_CIV_TEAMS; ++iTeam1)
		{
			if (GET_TEAM((TeamTypes)iTeam1).isFullMember(eVoteSource))
			{
				for (int iTeam2 = iTeam1 + 1; iTeam2 < MAX_CIV_TEAMS; ++iTeam2)
				{
					CvTeam& kTeam2 = GET_TEAM((TeamTypes)iTeam2);

					if (kTeam2.isFullMember(eVoteSource))
					{
						if (!kTeam2.isDefensivePact((TeamTypes)iTeam1))
						{
							bPactWithEveryone = false;
							break;
						}
					}
				}
			}
		}
		if (bPactWithEveryone)
		{
			return false;
		}
	}
	else if (GC.getVoteInfo(kData.eVote).isForcePeace())
	{
		CvPlayer& kPlayer = GET_PLAYER(kData.ePlayer);

		if (GET_TEAM(kPlayer.getTeam()).isAVassal())
		{
			return false;
		}

		if (!kPlayer.isFullMember(eVoteSource))
		{
			return false;
		}

		bool bValid = false;

		for (int iTeam2 = 0; iTeam2 < MAX_CIV_TEAMS; ++iTeam2)
		{
			if (atWar(kPlayer.getTeam(), (TeamTypes)iTeam2))
			{
				CvTeam& kTeam2 = GET_TEAM((TeamTypes)iTeam2);

				if (kTeam2.isVotingMember(eVoteSource))
				{
					bValid = true;
					break;
				}
			}
		}

		if (!bValid)
		{
			return false;
		}
	}
	else if (GC.getVoteInfo(kData.eVote).isForceNoTrade())
	{
		CvPlayer& kPlayer = GET_PLAYER(kData.ePlayer);

		if (kPlayer.isFullMember(eVoteSource))
		{
			return false;
		}

		bool bNoTradeWithEveryone = true;
		for (int iPlayer2 = 0; iPlayer2 < MAX_CIV_PLAYERS; ++iPlayer2)
		{
			CvPlayer& kPlayer2 = GET_PLAYER((PlayerTypes)iPlayer2);
			if (kPlayer2.getTeam() != kPlayer.getTeam())
			{
				if (kPlayer2.isFullMember(eVoteSource))
				{
					if (kPlayer2.canStopTradingWithTeam(kPlayer.getTeam()))
					{
						bNoTradeWithEveryone = false;
						break;
					}
				}
			}
		}
		// Not an option if already at war with everyone
		if (bNoTradeWithEveryone)
		{
			return false;
		}
	}
	else if (GC.getVoteInfo(kData.eVote).isForceWar())
	{
		CvPlayer& kPlayer = GET_PLAYER(kData.ePlayer);
		CvTeam& kTeam = GET_TEAM(kPlayer.getTeam());

		if (kTeam.isAVassal())
		{
			return false;
		}

		if (kPlayer.isFullMember(eVoteSource))
		{
			return false;
		}

		bool bAtWarWithEveryone = true;
		for (int iTeam2 = 0; iTeam2 < MAX_CIV_TEAMS; ++iTeam2)
		{
			if (iTeam2 != kPlayer.getTeam())
			{
				CvTeam& kTeam2 = GET_TEAM((TeamTypes)iTeam2);
				if (kTeam2.isFullMember(eVoteSource))
				{
					if (!kTeam2.isAtWar(kPlayer.getTeam()) && kTeam2.canChangeWarPeace(kPlayer.getTeam()))
					{
						bAtWarWithEveryone = false;
						break;
					}
				}
			}
		}
		// Not an option if already at war with everyone
		if (bAtWarWithEveryone)
		{
			return false;
		}

		// Can be passed against a non-member only if he is already at war with a member 
		if (!kPlayer.isVotingMember(eVoteSource))
		{
			bool bValid = false;
			for (int iTeam2 = 0; iTeam2 < MAX_CIV_TEAMS; ++iTeam2)
			{
				if (atWar(kPlayer.getTeam(), (TeamTypes)iTeam2))
				{
					CvTeam& kTeam2 = GET_TEAM((TeamTypes)iTeam2);

					if (kTeam2.isFullMember(eVoteSource))
					{
						bValid = true;
						break;
					}
				}
			}

			if (!bValid)
			{
				return false;
			}
		}
	}
	else if (GC.getVoteInfo(kData.eVote).isAssignCity())
	{
		CvPlayer& kPlayer = GET_PLAYER(kData.ePlayer);
		if (kPlayer.isFullMember(eVoteSource) || !kPlayer.isVotingMember(eVoteSource))
		{
			return false;
		}

		CvCity* pCity = kPlayer.getCity(kData.iCityId);
		FAssert(NULL != pCity);
		if (NULL == pCity)
		{
			return false;
		}

		if (NO_PLAYER == kData.eOtherPlayer)
		{
			return false;
		}

		CvPlayer& kOtherPlayer = GET_PLAYER(kData.eOtherPlayer);
		if (kOtherPlayer.getTeam() == kPlayer.getTeam())
		{
			return false;
		}

		if (atWar(kPlayer.getTeam(), GET_PLAYER(kData.eOtherPlayer).getTeam()))
		{
			return false;
		}

		if (!kOtherPlayer.isFullMember(eVoteSource))
		{
			return false;			
		}

		if (kOtherPlayer.isHuman() && isOption(GAMEOPTION_ONE_CITY_CHALLENGE))
		{
			return false;
		}
	}

	if (!canDoResolution(eVoteSource, kData))
	{
		return false;
	}

	return true;
}


bool CvGame::isDebugMode() const
{
	return m_bDebugModeCache;
}


void CvGame::toggleDebugMode()
{
	m_bDebugMode = ((m_bDebugMode) ? false : true);
	updateDebugModeCache();

	GC.getMapINLINE().updateVisibility();
	GC.getMapINLINE().updateSymbols();
	GC.getMapINLINE().updateMinimapColor();

	gDLL->getInterfaceIFace()->setDirty(GameData_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(Score_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(MinimapSection_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(UnitInfo_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(CityInfo_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(GlobeLayer_DIRTY_BIT, true);

	//gDLL->getEngineIFace()->SetDirty(GlobeTexture_DIRTY_BIT, true);
	gDLL->getEngineIFace()->SetDirty(MinimapTexture_DIRTY_BIT, true);
	gDLL->getEngineIFace()->SetDirty(CultureBorders_DIRTY_BIT, true);

	if (m_bDebugMode)
	{
		gDLL->getEngineIFace()->PushFogOfWar(FOGOFWARMODE_OFF);
	}
	else
	{
		gDLL->getEngineIFace()->PopFogOfWar();
	}
	gDLL->getEngineIFace()->setFogOfWarFromStack();
}

void CvGame::updateDebugModeCache()
{
	if ((gDLL->getChtLvl() > 0) || (gDLL->GetWorldBuilderMode()))
	{
		m_bDebugModeCache = m_bDebugMode;
	}
	else
	{
		m_bDebugModeCache = false;
	}
}

int CvGame::getPitbossTurnTime() const
{
	return GC.getInitCore().getPitbossTurnTime();
}

void CvGame::setPitbossTurnTime(int iHours)
{
	GC.getInitCore().setPitbossTurnTime(iHours);
}


bool CvGame::isHotSeat() const
{
	return (GC.getInitCore().getHotseat());
}

bool CvGame::isPbem() const
{
	return (GC.getInitCore().getPbem());
}



bool CvGame::isPitboss() const
{
	return (GC.getInitCore().getPitboss());
}

bool CvGame::isSimultaneousTeamTurns() const
{
	if (!isNetworkMultiPlayer())
	{
		return false;
	}

	if (isMPOption(MPOPTION_SIMULTANEOUS_TURNS))
	{
		return false;
	}
	
	return true;
}

bool CvGame::isFinalInitialized() const
{
	return m_bFinalInitialized;
}


void CvGame::setFinalInitialized(bool bNewValue)
{
	PROFILE_FUNC();

	int iI;

	if (isFinalInitialized() != bNewValue)
	{
		m_bFinalInitialized = bNewValue;

		if (isFinalInitialized())
		{
			updatePlotGroups();

			GC.getMapINLINE().updateIrrigated();

			for (iI = 0; iI < MAX_TEAMS; iI++)
			{
				if (GET_TEAM((TeamTypes)iI).isAlive())
				{
					GET_TEAM((TeamTypes)iI).AI_updateAreaStragies();
				}
			}
		}
	}
}


bool CvGame::getPbemTurnSent() const
{
	return m_bPbemTurnSent;
}


void CvGame::setPbemTurnSent(bool bNewValue)
{
	m_bPbemTurnSent = bNewValue;
}


bool CvGame::getHotPbemBetweenTurns() const
{
	return m_bHotPbemBetweenTurns;
}


void CvGame::setHotPbemBetweenTurns(bool bNewValue)
{
	m_bHotPbemBetweenTurns = bNewValue;
}


bool CvGame::isPlayerOptionsSent() const
{
	return m_bPlayerOptionsSent;
}


void CvGame::sendPlayerOptions(bool bForce)
{
	int iI;

	if (getActivePlayer() == NO_PLAYER)
	{
		return;
	}

	if (!isPlayerOptionsSent() || bForce)
	{
		m_bPlayerOptionsSent = true;

		for (iI = 0; iI < NUM_PLAYEROPTION_TYPES; iI++)
		{
			gDLL->sendPlayerOption(((PlayerOptionTypes)iI), gDLL->getPlayerOption((PlayerOptionTypes)iI));
		}
	}
}


PlayerTypes CvGame::getActivePlayer() const
{
	return GC.getInitCore().getActivePlayer();
}


void CvGame::setActivePlayer(PlayerTypes eNewValue, bool bForceHotSeat)
{
	PlayerTypes eOldActivePlayer = getActivePlayer();
	if (eOldActivePlayer != eNewValue)
	//if (eOldActivePlayer != eNewValue && !GET_PLAYER(eNewValue).isHuman()) //RFCMP
	{
		int iActiveNetId = ((NO_PLAYER != eOldActivePlayer) ? GET_PLAYER(eOldActivePlayer).getNetID() : -1);
		//Rhye - start (RFCMP)
		/*
		if (!(isHotSeat()  || isPbem()))// || bForceHotSeat))
		{
			GC.getInitCore().setSlotStatus(eOldActivePlayer, SS_COMPUTER);
			GC.getInitCore().setSlotStatus(eNewValue, SS_TAKEN);
		}*/
		//Rhye
		GC.getInitCore().setActivePlayer(eNewValue);

		if (GET_PLAYER(eNewValue).isHuman() && (isHotSeat() || isPbem() || bForceHotSeat))
		{
			gDLL->getPassword(eNewValue);
			setHotPbemBetweenTurns(false);
			gDLL->getInterfaceIFace()->dirtyTurnLog(eNewValue);

			if (NO_PLAYER != eOldActivePlayer)
			{
				int iInactiveNetId = GET_PLAYER(eNewValue).getNetID();
				GET_PLAYER(eNewValue).setNetID(iActiveNetId);
				GET_PLAYER(eOldActivePlayer).setNetID(iInactiveNetId);
			}

			GET_PLAYER(eNewValue).showMissedMessages();

			if (countHumanPlayersAlive() == 1 && isPbem())
			{
				// Nobody else left alive
				GC.getInitCore().setType(GAME_HOTSEAT_NEW);
			}

			sendPlayerOptions(true); //Rhye

			//Rhye - start (RFCMP)
			if (!(isHotSeat()  || isPbem() || bForceHotSeat))
			{
				long result = 0;
				CyArgsList argsList;
				argsList.add(eNewValue);
				gDLL->getPythonIFace()->callFunction(PYScreensModule, "resetStabilityParameters", argsList.makeFunctionArgs(), &result);
			}
			//Rhye - end

			if (isHotSeat() || bForceHotSeat)
			{
				sendPlayerOptions(true);
			}
		}

		if (GC.IsGraphicsInitialized())
		{
			GC.getMapINLINE().updateFog();
			GC.getMapINLINE().updateVisibility();
			GC.getMapINLINE().updateSymbols();
			GC.getMapINLINE().updateMinimapColor();

			updateUnitEnemyGlow();

			gDLL->getInterfaceIFace()->setEndTurnMessage(false);

			gDLL->getInterfaceIFace()->clearSelectedCities();
			gDLL->getInterfaceIFace()->clearSelectionList();

			gDLL->getInterfaceIFace()->setDirty(PercentButtons_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(ResearchButtons_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(GameData_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(MinimapSection_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(CityInfo_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(UnitInfo_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(Flag_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(GlobeLayer_DIRTY_BIT, true);

			gDLL->getEngineIFace()->SetDirty(CultureBorders_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(BlockadedPlots_DIRTY_BIT, true);

			
		}
	}
}

//Rhye - start (RFCMP)
//void CvGame::switchActivePlayer(int eOldPlayerNetID, PlayerTypes eNewValue, bool bForceHotSeat)
void CvGame::switchActivePlayer(PlayerTypes eOldActivePlayer, PlayerTypes eNewValue, bool bForceHotSeat)
{
	/*PlayerTypes eOldActivePlayer = getActivePlayer();

	for(int i=0;i<MAX_PLAYERS;i++)
	{
		if (GET_PLAYER((PlayerTypes)i).getNetID() == eOldPlayerNetID) {
			eOldActivePlayer = (PlayerTypes)i;
		}
	}*/

	if (eOldActivePlayer != eNewValue)
	{
		int iActiveNetId = ((NO_PLAYER != eOldActivePlayer) ? GET_PLAYER(eOldActivePlayer).getNetID() : -1);
		//Rhye - start (RFCMP - allow here on hotseat too)
		GC.getInitCore().setSlotStatus(eOldActivePlayer, SS_COMPUTER);
		GC.getInitCore().setSlotStatus(eNewValue, SS_TAKEN);
		//Rhye
		//if (eOldActivePlayer != getActivePlayer()) //RFCMP
		//		GC.getInitCore().setActivePlayer(eNewValue);

		if (GET_PLAYER(eNewValue).isHuman() && (isHotSeat() || isPbem() || bForceHotSeat))
		{
			gDLL->getPassword(eNewValue);
			setHotPbemBetweenTurns(false);
			gDLL->getInterfaceIFace()->dirtyTurnLog(eNewValue);

			if (NO_PLAYER != eOldActivePlayer)
			{
				int iInactiveNetId = GET_PLAYER(eNewValue).getNetID();
				GET_PLAYER(eNewValue).setNetID(iActiveNetId);
				GET_PLAYER(eOldActivePlayer).setNetID(iInactiveNetId);
			}

			GET_PLAYER(eNewValue).showMissedMessages();

			if (countHumanPlayersAlive() == 1 && isPbem())
			{
				// Nobody else left alive
				GC.getInitCore().setType(GAME_HOTSEAT_NEW);
			}

			sendPlayerOptions(true); //Rhye

			if (isHotSeat() || bForceHotSeat)
			{
				sendPlayerOptions(true);
			}
		}

		if (GC.IsGraphicsInitialized())
		{
			GC.getMapINLINE().updateFog();
			GC.getMapINLINE().updateVisibility();
			GC.getMapINLINE().updateSymbols();
			GC.getMapINLINE().updateMinimapColor();

			updateUnitEnemyGlow();

			gDLL->getInterfaceIFace()->setEndTurnMessage(false);

			gDLL->getInterfaceIFace()->clearSelectedCities();
			gDLL->getInterfaceIFace()->clearSelectionList();

			gDLL->getInterfaceIFace()->setDirty(PercentButtons_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(ResearchButtons_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(GameData_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(MinimapSection_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(CityInfo_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(UnitInfo_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(Flag_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(GlobeLayer_DIRTY_BIT, true);

			gDLL->getEngineIFace()->SetDirty(CultureBorders_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(BlockadedPlots_DIRTY_BIT, true);
		}
	}
}
//Rhye - end

void CvGame::updateUnitEnemyGlow()
{
	//update unit enemy glow
	for(int i=0;i<MAX_PLAYERS;i++)
	{
		PlayerTypes playerType = (PlayerTypes) i;
		int iLoop;
		for(CvUnit *pLoopUnit = GET_PLAYER(playerType).firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = GET_PLAYER(playerType).nextUnit(&iLoop))
		{
			//update glow
			gDLL->getEntityIFace()->updateEnemyGlow(pLoopUnit->getUnitEntity());
		}
	}
}

HandicapTypes CvGame::getHandicapType() const
{
	return m_eHandicap;
}

void CvGame::setHandicapType(HandicapTypes eHandicap)
{
	m_eHandicap = eHandicap;
}

PlayerTypes CvGame::getPausePlayer() const
{
	return m_ePausePlayer;
}


bool CvGame::isPaused() const
{
	return (getPausePlayer() != NO_PLAYER);
}


void CvGame::setPausePlayer(PlayerTypes eNewValue)
{
	m_ePausePlayer = eNewValue;
}


UnitTypes CvGame::getBestLandUnit() const
{
	return m_eBestLandUnit;
}


int CvGame::getBestLandUnitCombat() const
{
	if (getBestLandUnit() == NO_UNIT)
	{
		return 1;
	}

	return std::max(1, GC.getUnitInfo(getBestLandUnit()).getCombat());
}


void CvGame::setBestLandUnit(UnitTypes eNewValue)
{
	if (getBestLandUnit() != eNewValue)
	{
		m_eBestLandUnit = eNewValue;

		gDLL->getInterfaceIFace()->setDirty(UnitInfo_DIRTY_BIT, true);
	}
}


TeamTypes CvGame::getWinner() const
{
	return m_eWinner;
}


VictoryTypes CvGame::getVictory() const
{
	return m_eVictory;
}


void CvGame::setWinner(TeamTypes eNewWinner, VictoryTypes eNewVictory)
{
	CvWString szBuffer;

	if ((getWinner() != eNewWinner) || (getVictory() != eNewVictory))
	{
		m_eWinner = eNewWinner;
		m_eVictory = eNewVictory;

		if (getVictory() != NO_VICTORY)
		{
			if (getWinner() != NO_TEAM)
			{
				//Rhye - start
				//szBuffer = gDLL->getText("TXT_KEY_GAME_WON", GET_TEAM(getWinner()).getName().GetCString(), GC.getVictoryInfo(getVictory()).getTextKeyWide());
				szBuffer = gDLL->getText("TXT_KEY_GAME_WON", GET_PLAYER((PlayerTypes)getWinner()).getCivilizationShortDescription(), GC.getVictoryInfo(getVictory()).getTextKeyWide());
				//Rhye - end
				addReplayMessage(REPLAY_MESSAGE_MAJOR_EVENT, GET_TEAM(getWinner()).getLeaderID(), szBuffer, -1, -1, (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"));
			}

			if (isObserverAutoPlay() || (getAIAutoPlay() > 0) || gDLL->GetAutorun())
			{
				setGameState(GAMESTATE_EXTENDED);
			}
			else
			{
				setGameState(GAMESTATE_OVER);
			}
		}

		gDLL->getInterfaceIFace()->setDirty(Center_DIRTY_BIT, true);
		CvEventReporter::getInstance().victory(eNewWinner, eNewVictory);
		gDLL->getInterfaceIFace()->setDirty(Soundtrack_DIRTY_BIT, true);
	}
}


GameStateTypes CvGame::getGameState() const
{
	return m_eGameState;
}


void CvGame::setGameState(GameStateTypes eNewValue)
{
	CvPopupInfo* pInfo;
	int iI;

	if (getGameState() != eNewValue)
	{
		m_eGameState = eNewValue;

		if (eNewValue == GAMESTATE_OVER)
		{
			CvEventReporter::getInstance().gameEnd();

			showEndGameSequence();

			for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
			{
				if (GET_PLAYER((PlayerTypes)iI).isHuman())
				{
					// One more turn?
					pInfo = new CvPopupInfo(BUTTONPOPUP_EXTENDED_GAME);
					if (NULL != pInfo)
					{
						GET_PLAYER((PlayerTypes)iI).addPopup(pInfo);
					}
				}
			}
		}

		gDLL->getInterfaceIFace()->setDirty(Cursor_DIRTY_BIT, true);
	}
}


GameSpeedTypes CvGame::getGameSpeedType() const
{
	return GC.getInitCore().getGameSpeed();
}


EraTypes CvGame::getStartEra() const
{
	return GC.getInitCore().getEra();
}


CalendarTypes CvGame::getCalendar() const
{
	return GC.getInitCore().getCalendar();
}


PlayerTypes CvGame::getRankPlayer(int iRank) const																
{
	FAssertMsg(iRank >= 0, "iRank is expected to be non-negative (invalid Rank)");
	FAssertMsg(iRank < MAX_PLAYERS, "iRank is expected to be within maximum bounds (invalid Rank)");
	return (PlayerTypes)m_aiRankPlayer[iRank];
}


void CvGame::setRankPlayer(int iRank, PlayerTypes ePlayer)													
{
	FAssertMsg(iRank >= 0, "iRank is expected to be non-negative (invalid Rank)");
	FAssertMsg(iRank < MAX_PLAYERS, "iRank is expected to be within maximum bounds (invalid Rank)");

	if (getRankPlayer(iRank) != ePlayer)
	{
		m_aiRankPlayer[iRank] = ePlayer;

		gDLL->getInterfaceIFace()->setDirty(Score_DIRTY_BIT, true);
	}
}


int CvGame::getPlayerRank(PlayerTypes ePlayer) const														 
{
	FAssertMsg(ePlayer >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(ePlayer < MAX_PLAYERS, "ePlayer is expected to be within maximum bounds (invalid Index)");
	return m_aiPlayerRank[ePlayer];
}
 

void CvGame::setPlayerRank(PlayerTypes ePlayer, int iRank)													
{
	FAssertMsg(ePlayer >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(ePlayer < MAX_PLAYERS, "ePlayer is expected to be within maximum bounds (invalid Index)");
	m_aiPlayerRank[ePlayer] = iRank;
	FAssert(getPlayerRank(ePlayer) >= 0);
}


int CvGame::getPlayerScore(PlayerTypes ePlayer)	const																
{
	FAssertMsg(ePlayer >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(ePlayer < MAX_PLAYERS, "ePlayer is expected to be within maximum bounds (invalid Index)");
	return m_aiPlayerScore[ePlayer];
}


void CvGame::setPlayerScore(PlayerTypes ePlayer, int iScore)													
{
	FAssertMsg(ePlayer >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(ePlayer < MAX_PLAYERS, "ePlayer is expected to be within maximum bounds (invalid Index)");

	if (getPlayerScore(ePlayer) != iScore)
	{
		m_aiPlayerScore[ePlayer] = iScore;
		FAssert(getPlayerScore(ePlayer) >= 0);

		gDLL->getInterfaceIFace()->setDirty(Score_DIRTY_BIT, true);
	}
}


TeamTypes CvGame::getRankTeam(int iRank) const																	
{
	FAssertMsg(iRank >= 0, "iRank is expected to be non-negative (invalid Rank)");
	FAssertMsg(iRank < MAX_TEAMS, "iRank is expected to be within maximum bounds (invalid Index)");
	return (TeamTypes)m_aiRankTeam[iRank];
}


void CvGame::setRankTeam(int iRank, TeamTypes eTeam)														
{
	FAssertMsg(iRank >= 0, "iRank is expected to be non-negative (invalid Rank)");
	FAssertMsg(iRank < MAX_TEAMS, "iRank is expected to be within maximum bounds (invalid Index)");

	if (getRankTeam(iRank) != eTeam)
	{
		m_aiRankTeam[iRank] = eTeam;

		gDLL->getInterfaceIFace()->setDirty(Score_DIRTY_BIT, true);
	}
}


int CvGame::getTeamRank(TeamTypes eTeam) const																	
{
	FAssertMsg(eTeam >= 0, "eTeam is expected to be non-negative (invalid Index)");
	FAssertMsg(eTeam < MAX_TEAMS, "eTeam is expected to be within maximum bounds (invalid Index)");
	return m_aiTeamRank[eTeam];
}


void CvGame::setTeamRank(TeamTypes eTeam, int iRank)														
{
	FAssertMsg(eTeam >= 0, "eTeam is expected to be non-negative (invalid Index)");
	FAssertMsg(eTeam < MAX_TEAMS, "eTeam is expected to be within maximum bounds (invalid Index)");
	m_aiTeamRank[eTeam] = iRank;
	FAssert(getTeamRank(eTeam) >= 0);
}


int CvGame::getTeamScore(TeamTypes eTeam) const																	
{
	FAssertMsg(eTeam >= 0, "eTeam is expected to be non-negative (invalid Index)");
	FAssertMsg(eTeam < MAX_TEAMS, "eTeam is expected to be within maximum bounds (invalid Index)");
	return m_aiTeamScore[eTeam];
}


void CvGame::setTeamScore(TeamTypes eTeam, int iScore)		
{
	FAssertMsg(eTeam >= 0, "eTeam is expected to be non-negative (invalid Index)");
	FAssertMsg(eTeam < MAX_TEAMS, "eTeam is expected to be within maximum bounds (invalid Index)");
	m_aiTeamScore[eTeam] = iScore;
	FAssert(getTeamScore(eTeam) >= 0);
}


bool CvGame::isOption(GameOptionTypes eIndex) const
{
	return GC.getInitCore().getOption(eIndex);
}


void CvGame::setOption(GameOptionTypes eIndex, bool bEnabled)
{
	GC.getInitCore().setOption(eIndex, bEnabled);
}


bool CvGame::isMPOption(MultiplayerOptionTypes eIndex) const
{
	return GC.getInitCore().getMPOption(eIndex);
}


void CvGame::setMPOption(MultiplayerOptionTypes eIndex, bool bEnabled)
{
	GC.getInitCore().setMPOption(eIndex, bEnabled);
}


bool CvGame::isForcedControl(ForceControlTypes eIndex) const
{
	return GC.getInitCore().getForceControl(eIndex);
}


void CvGame::setForceControl(ForceControlTypes eIndex, bool bEnabled)
{
	GC.getInitCore().setForceControl(eIndex, bEnabled);
}


int CvGame::getUnitCreatedCount(UnitTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumUnitInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiUnitCreatedCount[eIndex];
}


void CvGame::incrementUnitCreatedCount(UnitTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumUnitInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	m_paiUnitCreatedCount[eIndex]++;
}


int CvGame::getUnitClassCreatedCount(UnitClassTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumUnitClassInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiUnitClassCreatedCount[eIndex];
}


bool CvGame::isUnitClassMaxedOut(UnitClassTypes eIndex, int iExtra)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumUnitClassInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (!isWorldUnitClass(eIndex))
	{
		return false;
	}

	FAssertMsg(getUnitClassCreatedCount(eIndex) <= GC.getUnitClassInfo(eIndex).getMaxGlobalInstances(), "Index is expected to be within maximum bounds (invalid Index)");

	return ((getUnitClassCreatedCount(eIndex) + iExtra) >= GC.getUnitClassInfo(eIndex).getMaxGlobalInstances());
}


void CvGame::incrementUnitClassCreatedCount(UnitClassTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumUnitClassInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	m_paiUnitClassCreatedCount[eIndex]++;
}


int CvGame::getBuildingClassCreatedCount(BuildingClassTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumBuildingClassInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiBuildingClassCreatedCount[eIndex];
}


bool CvGame::isBuildingClassMaxedOut(BuildingClassTypes eIndex, int iExtra)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumBuildingClassInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (!isWorldWonderClass(eIndex))
	{
		return false;
	}

	FAssertMsg(getBuildingClassCreatedCount(eIndex) <= GC.getBuildingClassInfo(eIndex).getMaxGlobalInstances(), "Index is expected to be within maximum bounds (invalid Index)");

	return ((getBuildingClassCreatedCount(eIndex) + iExtra) >= GC.getBuildingClassInfo(eIndex).getMaxGlobalInstances());
}


void CvGame::incrementBuildingClassCreatedCount(BuildingClassTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumBuildingClassInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	m_paiBuildingClassCreatedCount[eIndex]++;
}


int CvGame::getProjectCreatedCount(ProjectTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumProjectInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiProjectCreatedCount[eIndex];
}


bool CvGame::isProjectMaxedOut(ProjectTypes eIndex, int iExtra)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumProjectInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (!isWorldProject(eIndex))
	{
		return false;
	}

	FAssertMsg(getProjectCreatedCount(eIndex) <= GC.getProjectInfo(eIndex).getMaxGlobalInstances(), "Index is expected to be within maximum bounds (invalid Index)");

	return ((getProjectCreatedCount(eIndex) + iExtra) >= GC.getProjectInfo(eIndex).getMaxGlobalInstances());
}


void CvGame::incrementProjectCreatedCount(ProjectTypes eIndex, int iExtra)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumProjectInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	m_paiProjectCreatedCount[eIndex] += iExtra;
}


int CvGame::getForceCivicCount(CivicTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumCivicInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiForceCivicCount[eIndex];
}


bool CvGame::isForceCivic(CivicTypes eIndex) const
{
	return (getForceCivicCount(eIndex) > 0);
}


bool CvGame::isForceCivicOption(CivicOptionTypes eCivicOption) const
{
	int iI;

	for (iI = 0; iI < GC.getNumCivicInfos(); iI++)
	{
		if (GC.getCivicInfo((CivicTypes)iI).getCivicOptionType() == eCivicOption)
		{
			if (isForceCivic((CivicTypes)iI))
			{
				return true;
			}
		}
	}

	return false;
}


void CvGame::changeForceCivicCount(CivicTypes eIndex, int iChange)
{
	bool bOldForceCivic;

	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumCivicInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (iChange != 0)
	{
		bOldForceCivic = isForceCivic(eIndex);

		m_paiForceCivicCount[eIndex] += iChange;
		FAssert(getForceCivicCount(eIndex) >= 0);

		if (bOldForceCivic != isForceCivic(eIndex))
		{
			verifyCivics();
		}
	}
}


PlayerVoteTypes CvGame::getVoteOutcome(VoteTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumVoteInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiVoteOutcome[eIndex];
}


bool CvGame::isVotePassed(VoteTypes eIndex) const
{
	PlayerVoteTypes ePlayerVote = getVoteOutcome(eIndex);

	if (isTeamVote(eIndex))
	{
		return (ePlayerVote >= 0 && ePlayerVote < MAX_CIV_TEAMS);
	}
	else
	{
		return (ePlayerVote == PLAYER_VOTE_YES);
	}
}


void CvGame::setVoteOutcome(const VoteTriggeredData& kData, PlayerVoteTypes eNewValue)
{
	bool bOldPassed;

	VoteTypes eIndex = kData.kVoteOption.eVote;
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumVoteInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (getVoteOutcome(eIndex) != eNewValue)
	{
		bOldPassed = isVotePassed(eIndex);

		m_paiVoteOutcome[eIndex] = eNewValue;

		if (bOldPassed != isVotePassed(eIndex))
		{
			processVote(kData, ((isVotePassed(eIndex)) ? 1 : -1));
		}
	}

	for (int iPlayer = 0; iPlayer < MAX_CIV_PLAYERS; ++iPlayer)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)iPlayer);
		if (kPlayer.isAlive())
		{
			kPlayer.setVote(kData.getID(), NO_PLAYER_VOTE);
		}
	}
}


int CvGame::getReligionGameTurnFounded(ReligionTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumReligionInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiReligionGameTurnFounded[eIndex];
}


bool CvGame::isReligionFounded(ReligionTypes eIndex)
{
	return (getReligionGameTurnFounded(eIndex) != -1);
}


void CvGame::makeReligionFounded(ReligionTypes eIndex, PlayerTypes ePlayer)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumReligionInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (!isReligionFounded(eIndex))
	{
		FAssertMsg(getGameTurn() != -1, "getGameTurn() is not expected to be equal with -1");
		m_paiReligionGameTurnFounded[eIndex] = getGameTurn();

		CvEventReporter::getInstance().religionFounded(eIndex, ePlayer);
	}
}

bool CvGame::isReligionSlotTaken(ReligionTypes eReligion) const
{
	FAssertMsg(eReligion >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eReligion < GC.getNumReligionInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_abReligionSlotTaken[eReligion];
}

void CvGame::setReligionSlotTaken(ReligionTypes eReligion, bool bTaken)
{
	FAssertMsg(eReligion >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eReligion < GC.getNumReligionInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	m_abReligionSlotTaken[eReligion] = bTaken;
}


int CvGame::getCorporationGameTurnFounded(CorporationTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumCorporationInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiCorporationGameTurnFounded[eIndex];
}


bool CvGame::isCorporationFounded(CorporationTypes eIndex)
{
	return (getCorporationGameTurnFounded(eIndex) != -1);
}


void CvGame::makeCorporationFounded(CorporationTypes eIndex, PlayerTypes ePlayer)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumCorporationInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (!isCorporationFounded(eIndex))
	{
		FAssertMsg(getGameTurn() != -1, "getGameTurn() is not expected to be equal with -1");
		m_paiCorporationGameTurnFounded[eIndex] = getGameTurn();

		CvEventReporter::getInstance().corporationFounded(eIndex, ePlayer);
	}
}

bool CvGame::isVictoryValid(VictoryTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumVictoryInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return GC.getInitCore().getVictory(eIndex);
}

void CvGame::setVictoryValid(VictoryTypes eIndex, bool bValid)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumVictoryInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	GC.getInitCore().setVictory(eIndex, bValid);
}


bool CvGame::isSpecialUnitValid(SpecialUnitTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumSpecialUnitInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_pabSpecialUnitValid[eIndex];
}


void CvGame::makeSpecialUnitValid(SpecialUnitTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumSpecialUnitInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	m_pabSpecialUnitValid[eIndex] = true;
}


bool CvGame::isSpecialBuildingValid(SpecialBuildingTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumSpecialBuildingInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_pabSpecialBuildingValid[eIndex];
}


void CvGame::makeSpecialBuildingValid(SpecialBuildingTypes eIndex, bool bAnnounce)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumSpecialBuildingInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (!m_pabSpecialBuildingValid[eIndex])
	{
		m_pabSpecialBuildingValid[eIndex] = true;


		if (bAnnounce)
		{
			CvWString szBuffer = gDLL->getText("TXT_KEY_SPECIAL_BUILDING_VALID", GC.getSpecialBuildingInfo(eIndex).getTextKeyWide());

			for (int iI = 0; iI < MAX_PLAYERS; iI++)
			{
				if (GET_PLAYER((PlayerTypes)iI).isAlive())
				{
					gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_PROJECT_COMPLETED", MESSAGE_TYPE_MAJOR_EVENT, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"));
				}
			}
		}
	}
}


bool CvGame::isNukesValid() const
{
	return m_bNukesValid;
}


void CvGame::makeNukesValid(bool bValid)
{
	m_bNukesValid = bValid;
}

bool CvGame::isInAdvancedStart() const
{
	for (int iPlayer = 0; iPlayer < MAX_PLAYERS; ++iPlayer)
	{
		if ((GET_PLAYER((PlayerTypes)iPlayer).getAdvancedStartPoints() >= 0) && GET_PLAYER((PlayerTypes)iPlayer).isHuman())
		{
			return true;
		}
	}

	return false;
}

void CvGame::setVoteChosen(int iSelection, int iVoteId)
{
	VoteSelectionData* pVoteSelectionData = getVoteSelection(iVoteId);
	if (NULL != pVoteSelectionData)
	{
		if (!isApostolicCouncil(pVoteSelectionData->eVoteSource) ||
			(isCouncilActive() && getCouncilVoteId() < 0 && iSelection >= 0 && iSelection < (int)pVoteSelectionData->aVoteOptions.size() && canCouncilPropose(pVoteSelectionData->aVoteOptions[iSelection])))
			addVoteTriggered(*pVoteSelectionData, iSelection);
	}

	deleteVoteSelection(iVoteId);
}


CvCity* CvGame::getHolyCity(ReligionTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumReligionInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return getCity(m_paHolyCity[eIndex]);
}


// Founding Christianity establishes a small coastal foothold. This is confined
// to the RFC Mediterranean basin, excluding the Black Sea, Red Sea and Atlantic.
static void seedChristianMediterraneanCities(CvCity* pHolyCity)
{
    const ReligionTypes eReligion = (ReligionTypes)GC.getInfoTypeForString("RELIGION_CHRISTIANITY");
    const CivicTypes eAtheism = (CivicTypes)GC.getInfoTypeForString("CIVIC_STATE_ATHEISM");
    std::vector<bool> abMediterranean(GC.getMapINLINE().numPlotsINLINE(), false);
    std::vector<CvPlot*> apWater;
    CvPlot* pSeed = GC.getMapINLINE().plotINLINE(60, 39);
    if (pSeed == NULL || !pSeed->isWater()) return;
    apWater.push_back(pSeed);
    abMediterranean[GC.getMapINLINE().plotNum(60, 39)] = true;
    for (int i = 0; i < (int)apWater.size(); ++i)
    {
        CvPlot* pPlot = apWater[i];
        for (int j = 0; j < NUM_CARDINALDIRECTION_TYPES; ++j)
        {
            CvPlot* pNext = plotCardinalDirection(pPlot->getX_INLINE(), pPlot->getY_INLINE(), (CardinalDirectionTypes)j);
            if (pNext == NULL || !pNext->isWater()) continue;
            const int x = pNext->getX_INLINE(), y = pNext->getY_INLINE();
            if (x < 52 || x > 74 || y < 37 || y > 45 || (x >= 69 && y >= 44)) continue;
            const int iIndex = GC.getMapINLINE().plotNum(x, y);
            if (!abMediterranean[iIndex])
            {
                abMediterranean[iIndex] = true;
                apWater.push_back(pNext);
            }
        }
    }
    const int iCount = std::max(0, GC.getDefineINT("RFCMP_CHRISTIANITY_INITIAL_COASTAL_CITIES"));
    for (int i = 0; i < iCount; ++i)
    {
        CvCity* pBestCity = NULL;
        int iBestDistance = MAX_INT;
        // Map-index ordering breaks equal-distance ties identically on all peers.
        for (int j = 0; j < GC.getMapINLINE().numPlotsINLINE(); ++j)
        {
            CvCity* pCity = GC.getMapINLINE().plotByIndexINLINE(j)->getPlotCity();
            if (pCity == NULL || pCity == pHolyCity || pCity->isHasReligion(eReligion) || pCity->isReligionBanned(eReligion)) continue;
            CvPlayer& kOwner = GET_PLAYER(pCity->getOwnerINLINE());
            if (!kOwner.isAlive() || kOwner.isCivic(eAtheism) || (kOwner.isNoNonStateReligionSpread() && kOwner.getStateReligion() != eReligion)) continue;
            bool bMediterraneanCoast = false;
            for (int k = 0; k < NUM_DIRECTION_TYPES; ++k)
            {
                CvPlot* pAdjacent = plotDirection(pCity->getX_INLINE(), pCity->getY_INLINE(), (DirectionTypes)k);
                if (pAdjacent != NULL && abMediterranean[GC.getMapINLINE().plotNum(pAdjacent->getX_INLINE(), pAdjacent->getY_INLINE())])
                    bMediterraneanCoast = true;
            }
            if (!bMediterraneanCoast) continue;
            const int iDistance = plotDistance(pHolyCity->getX_INLINE(), pHolyCity->getY_INLINE(), pCity->getX_INLINE(), pCity->getY_INLINE());
            if (iDistance < iBestDistance)
            {
                iBestDistance = iDistance;
                pBestCity = pCity;
            }
        }
        if (pBestCity == NULL) break;
        pBestCity->spreadReligion(eReligion, true);
    }
}

void CvGame::setHolyCity(ReligionTypes eIndex, CvCity* pNewValue, bool bAnnounce, bool bSpreadReligion)
{
	CvWString szBuffer;
	CvCity* pOldValue;
	CvCity* pHolyCity;
	int iI;

	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumReligionInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	const bool bNewReligion = !isReligionFounded(eIndex);
	pOldValue = getHolyCity(eIndex);

	if (pOldValue != pNewValue)
	{
		  // religion visibility now part of espionage
		//updateCitySight(false, true);

		if (pNewValue != NULL)
		{
			m_paHolyCity[eIndex] = pNewValue->getIDInfo();
		}
		else
		{
			m_paHolyCity[eIndex].reset();
		}

		// religion visibility now part of espionage
		//updateCitySight(true, true);

		if (pOldValue != NULL)
		{
			pOldValue->changeReligionInfluence(eIndex, -(GC.getDefineINT("HOLY_CITY_INFLUENCE")));

			pOldValue->updateReligionCommerce();

			pOldValue->setInfoDirty(true);
		}

		if (getHolyCity(eIndex) != NULL)
		{
			pHolyCity = getHolyCity(eIndex);

			// Persist the owner-scoped choice before adding Islam, suppressing the
			// ordinary conversion popup until this founding decision is resolved.
            const bool bIslamFounding = bSpreadReligion && bNewReligion &&
                eIndex == (ReligionTypes)GC.getInfoTypeForString("RELIGION_ISLAM");
            if (bIslamFounding) GET_PLAYER(pHolyCity->getOwnerINLINE()).prepareIslamFounding();
			if (bSpreadReligion) pHolyCity->setHasReligion(eIndex, true, bAnnounce, true, true);
			pHolyCity->changeReligionInfluence(eIndex, GC.getDefineINT("HOLY_CITY_INFLUENCE"));

			pHolyCity->updateReligionCommerce();

			pHolyCity->setInfoDirty(true);
            if (bSpreadReligion && bNewReligion && eIndex == (ReligionTypes)GC.getInfoTypeForString("RELIGION_CHRISTIANITY"))
                seedChristianMediterraneanCities(pHolyCity);
            if (bIslamFounding) GET_PLAYER(pHolyCity->getOwnerINLINE()).processIslamFounding();

			if (bAnnounce)
			{
				if (isFinalInitialized() && !(gDLL->GetWorldBuilderMode()))
				{
					szBuffer = gDLL->getText("TXT_KEY_MISC_REL_FOUNDED", GC.getReligionInfo(eIndex).getTextKeyWide(), pHolyCity->getNameKey());
					addReplayMessage(REPLAY_MESSAGE_MAJOR_EVENT, pHolyCity->getOwnerINLINE(), szBuffer, pHolyCity->getX_INLINE(), pHolyCity->getY_INLINE(), (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"));

					for (iI = 0; iI < MAX_PLAYERS; iI++)
					{
						if (GET_PLAYER((PlayerTypes)iI).isAlive())
						{
							if (pHolyCity->isRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false))
							{
								szBuffer = gDLL->getText("TXT_KEY_MISC_REL_FOUNDED", GC.getReligionInfo(eIndex).getTextKeyWide(), pHolyCity->getNameKey());
								gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getDefineINT("EVENT_MESSAGE_TIME_LONG"), szBuffer, GC.getReligionInfo(eIndex).getSound(), MESSAGE_TYPE_MAJOR_EVENT, GC.getReligionInfo(eIndex).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"), pHolyCity->getX_INLINE(), pHolyCity->getY_INLINE());
							}
							else
							{
								szBuffer = gDLL->getText("TXT_KEY_MISC_REL_FOUNDED_UNKNOWN", GC.getReligionInfo(eIndex).getTextKeyWide());
								gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getDefineINT("EVENT_MESSAGE_TIME_LONG"), szBuffer, GC.getReligionInfo(eIndex).getSound(), MESSAGE_TYPE_MAJOR_EVENT, GC.getReligionInfo(eIndex).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"));
							}
						}
					}
				}
			}
		}

		AI_makeAssignWorkDirty();
	}
}


CvCity* CvGame::getHeadquarters(CorporationTypes eIndex)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumCorporationInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return getCity(m_paHeadquarters[eIndex]);
}


void CvGame::setHeadquarters(CorporationTypes eIndex, CvCity* pNewValue, bool bAnnounce)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumCorporationInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	CvCity* pOldValue = getHeadquarters(eIndex);

	if (pOldValue != pNewValue)
	{
		if (pNewValue != NULL)
		{
			m_paHeadquarters[eIndex] = pNewValue->getIDInfo();
		}
		else
		{
			m_paHeadquarters[eIndex].reset();
		}

		if (pOldValue != NULL)
		{
			pOldValue->updateCorporation();

			pOldValue->setInfoDirty(true);
		}

		CvCity* pHeadquarters = getHeadquarters(eIndex);

		if (NULL != pHeadquarters)
		{
			pHeadquarters->setHasCorporation(eIndex, true, bAnnounce);
			pHeadquarters->updateCorporation();
			pHeadquarters->setInfoDirty(true);

			if (bAnnounce)
			{
				if (isFinalInitialized() && !(gDLL->GetWorldBuilderMode()))
				{
					CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_CORPORATION_FOUNDED", GC.getCorporationInfo(eIndex).getTextKeyWide(), pHeadquarters->getNameKey());
					addReplayMessage(REPLAY_MESSAGE_MAJOR_EVENT, pHeadquarters->getOwnerINLINE(), szBuffer, pHeadquarters->getX_INLINE(), pHeadquarters->getY_INLINE(), (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"));

					for (int iI = 0; iI < MAX_PLAYERS; iI++)
					{
						if (GET_PLAYER((PlayerTypes)iI).isAlive())
						{
							if (pHeadquarters->isRevealed(GET_PLAYER((PlayerTypes)iI).getTeam(), false))
							{
								gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getDefineINT("EVENT_MESSAGE_TIME_LONG"), szBuffer, GC.getCorporationInfo(eIndex).getSound(), MESSAGE_TYPE_MAJOR_EVENT, GC.getCorporationInfo(eIndex).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"), pHeadquarters->getX_INLINE(), pHeadquarters->getY_INLINE());
							}
							else
							{
								CvWString szBuffer2 = gDLL->getText("TXT_KEY_MISC_CORPORATION_FOUNDED_UNKNOWN", GC.getCorporationInfo(eIndex).getTextKeyWide());
								gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getDefineINT("EVENT_MESSAGE_TIME_LONG"), szBuffer2, GC.getCorporationInfo(eIndex).getSound(), MESSAGE_TYPE_MAJOR_EVENT, GC.getCorporationInfo(eIndex).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"));
							}
						}
					}
				}
			}
		}

		AI_makeAssignWorkDirty();
	}
}


PlayerVoteTypes CvGame::getPlayerVote(PlayerTypes eOwnerIndex, int iVoteId) const
{
	FAssert(eOwnerIndex >= 0);
	FAssert(eOwnerIndex < MAX_CIV_PLAYERS);
	FAssert(NULL != getVoteTriggered(iVoteId));

	return GET_PLAYER(eOwnerIndex).getVote(iVoteId);
}


void CvGame::setPlayerVote(PlayerTypes eOwnerIndex, int iVoteId, PlayerVoteTypes eNewValue)
{
	FAssert(eOwnerIndex >= 0);
	FAssert(eOwnerIndex < MAX_CIV_PLAYERS);
	FAssert(NULL != getVoteTriggered(iVoteId));

	GET_PLAYER(eOwnerIndex).setVote(iVoteId, eNewValue);
#if ARFC_ENABLE_REPORTING
	VoteTriggeredData* pCouncil = getVoteTriggered(iVoteId);
	if (pCouncil && isApostolicCouncil(pCouncil->eVoteSource) && eNewValue != NO_PLAYER_VOTE)
		reportApostolicMechanic("council_vote", eOwnerIndex, iVoteId, eNewValue, pCouncil->aiCouncilWeight[eOwnerIndex], pCouncil->iCouncilDeadline);
#endif
}


void CvGame::castVote(PlayerTypes eOwnerIndex, int iVoteId, PlayerVoteTypes ePlayerVote)
{
	VoteTriggeredData* pTriggeredData = getVoteTriggered(iVoteId);
	if (pTriggeredData && isApostolicCouncil(pTriggeredData->eVoteSource))
	{
		if (!isCouncilActive() || eOwnerIndex < 0 || eOwnerIndex >= MAX_CIV_PLAYERS || pTriggeredData->aiCouncilWeight[eOwnerIndex] <= 0 ||
			pTriggeredData->aiCouncilDelivery[eOwnerIndex] >= 0 || getGameTurn() >= pTriggeredData->iCouncilDeadline ||
			getPlayerVote(eOwnerIndex, iVoteId) != NO_PLAYER_VOTE || !GET_PLAYER(eOwnerIndex).isVotingMember(pTriggeredData->eVoteSource) ||
			(ePlayerVote != PLAYER_VOTE_YES && ePlayerVote != PLAYER_VOTE_NO && ePlayerVote != PLAYER_VOTE_ABSTAIN)) return;
	}
	if (NULL != pTriggeredData)
	{
		CvVoteInfo& kVote = GC.getVoteInfo(pTriggeredData->kVoteOption.eVote);
		if (kVote.isAssignCity())
		{
			FAssert(pTriggeredData->kVoteOption.ePlayer != NO_PLAYER);
			CvPlayer& kCityPlayer = GET_PLAYER(pTriggeredData->kVoteOption.ePlayer);

			if (GET_PLAYER(eOwnerIndex).getTeam() != kCityPlayer.getTeam())
			{
				switch (ePlayerVote)
				{
				case PLAYER_VOTE_YES:
					kCityPlayer.AI_changeMemoryCount(eOwnerIndex, MEMORY_VOTED_AGAINST_US, 1);
					break;
				case PLAYER_VOTE_NO:
					kCityPlayer.AI_changeMemoryCount(eOwnerIndex, MEMORY_VOTED_FOR_US, 1);
					break;
				default:
					break;
				}
			}
		}
		else if (isTeamVote(pTriggeredData->kVoteOption.eVote))
		{
			if ((PlayerVoteTypes)GET_PLAYER(eOwnerIndex).getTeam() != ePlayerVote)
			{
				for (int iPlayer = 0; iPlayer < MAX_CIV_PLAYERS; ++iPlayer)
				{
					CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iPlayer);
					if (kLoopPlayer.isAlive())
					{
						if (kLoopPlayer.getTeam() != GET_PLAYER(eOwnerIndex).getTeam() && kLoopPlayer.getTeam() == (TeamTypes)ePlayerVote)
						{
							kLoopPlayer.AI_changeMemoryCount(eOwnerIndex, MEMORY_VOTED_FOR_US, 1);
						}
					}
				}
			}
		}

		setPlayerVote(eOwnerIndex, iVoteId, ePlayerVote);
	}
}


std::string CvGame::getScriptData() const
{
	return m_szScriptData;
}


void CvGame::setScriptData(std::string szNewValue)
{
	m_szScriptData = szNewValue;
}

const CvWString & CvGame::getName()
{
	return GC.getInitCore().getGameName();
}


void CvGame::setName(const TCHAR* szName)
{
	GC.getInitCore().setGameName(szName);
}


bool CvGame::isDestroyedCityName(CvWString& szName) const
{
	std::vector<CvWString>::const_iterator it;

	for (it = m_aszDestroyedCities.begin(); it != m_aszDestroyedCities.end(); it++)
	{
		if (*it == szName)
		{
			return true;
		}
	}

	return false;
}

void CvGame::addDestroyedCityName(const CvWString& szName)
{
	m_aszDestroyedCities.push_back(szName);
}

bool CvGame::isGreatPersonBorn(CvWString& szName) const
{
	std::vector<CvWString>::const_iterator it;

	for (it = m_aszGreatPeopleBorn.begin(); it != m_aszGreatPeopleBorn.end(); it++)
	{
		if (*it == szName)
		{
			return true;
		}
	}

	return false;
}

void CvGame::addGreatPersonBornName(const CvWString& szName)
{
	m_aszGreatPeopleBorn.push_back(szName);
}


// Protected Functions...

void CvGame::doTurn()
{
	doCrusade();
	doPapalFounding();
	observerPerformanceFlush();
	OBSERVER_PERFORMANCE("game.doTurn");
	PROFILE_BEGIN("CvGame::doTurn()");
	//logMsg("doTurn"); //Rhye
	int aiShuffle[MAX_PLAYERS];
	int iLoopPlayer;
	int iI;

	//Rhye - start
	for (iI = 0; iI < MAX_PLAYERS; iI++)
		turnPlayed[iI] = 0;
	//Rhye - end

	// Keep observer UI bounded: clear old combat/resource notification icons.
	if (isObserverAutoPlay()) gDLL->getInterfaceIFace()->clearEventMessages();

	// END OF TURN
	CvEventReporter::getInstance().beginGameTurn( getGameTurn() );
    // Check even dead players so expiry and announcements are never stranded.
    for (int iJihadPlayer = 0; iJihadPlayer < MAX_PLAYERS; ++iJihadPlayer)
        GET_PLAYER((PlayerTypes)iJihadPlayer).doArabianJihad();

	doUpdateCacheOnTurn();

	updateScore();

	doDeals();

	for (iI = 0; iI < MAX_TEAMS; iI++)
	{
		if (GET_TEAM((TeamTypes)iI).isAlive())
		{
			GET_TEAM((TeamTypes)iI).doTurn();
		}
	}

	GC.getMapINLINE().doTurn();

	//Rhye
	//createBarbarianCities();

	createBarbarianUnits();


	//Rhye - comment this to stop religion founding
	doHolyCity();

	doHeadquarters();

	doDiploVote();

	gDLL->getInterfaceIFace()->setEndTurnMessage(false);
	gDLL->getInterfaceIFace()->setHasMovedUnit(false);

	if (getAIAutoPlay() > 0)
	{
		changeAIAutoPlay(-1);

		if (getAIAutoPlay() == 0)
		{
			reviveActivePlayer();
		}
	}


#if ARFC_ENABLE_REPORTING
	reportApostolicState();
#endif
	CvEventReporter::getInstance().endGameTurn(getGameTurn());

	incrementGameTurn();
	incrementElapsedGameTurns();

    updateTradeRoutes();
    updateFoodTrade();

	if (isMPOption(MPOPTION_SIMULTANEOUS_TURNS))
	{
		shuffleArray(aiShuffle, MAX_PLAYERS, getSorenRand());

		for (iI = 0; iI < MAX_PLAYERS; iI++)
		{
			iLoopPlayer = aiShuffle[iI];

			if (GET_PLAYER((PlayerTypes)iLoopPlayer).isAlive())
			{
				GET_PLAYER((PlayerTypes)iLoopPlayer).setTurnActive(true);
			}
		}
	}
	else if (isSimultaneousTeamTurns())
	{
		for (iI = 0; iI < MAX_TEAMS; iI++)
		{
			CvTeam& kTeam = GET_TEAM((TeamTypes)iI);
			if (kTeam.isAlive())
			{
				kTeam.setTurnActive(true);
				FAssert(getNumGameTurnActive() == kTeam.getAliveCount());
			}

			break;
		}
	}
	else
	{
		for (iI = 0; iI < MAX_PLAYERS; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive())
			{
				if (isPbem() && GET_PLAYER((PlayerTypes)iI).isHuman())
				{
					if (iI == getActivePlayer())
					{
						// Nobody else left alive
						GC.getInitCore().setType(GAME_HOTSEAT_NEW);
						GET_PLAYER((PlayerTypes)iI).setTurnActive(true);
					}
					else if (!getPbemTurnSent())
					{
						gDLL->sendPbemTurn((PlayerTypes)iI);
					}
				}
				else
				{
					GET_PLAYER((PlayerTypes)iI).setTurnActive(true);
					FAssert(getNumGameTurnActive() == 1);
				}

				break;
			}
		}
	}

	testVictory();

	gDLL->getEngineIFace()->SetDirty(GlobePartialTexture_DIRTY_BIT, true);
	gDLL->getEngineIFace()->DoTurn();

	PROFILE_END();

	stopProfilingDLL();

	if (!isObserverNoAutosaves()) gDLL->getEngineIFace()->AutoSave();
}


void CvGame::doDeals()
{
	OBSERVER_PERFORMANCE("CvGame::doDeals");
	CvDeal* pLoopDeal;
	int iLoop;

	verifyDeals();

	for(pLoopDeal = firstDeal(&iLoop); pLoopDeal != NULL; pLoopDeal = nextDeal(&iLoop))
	{
		pLoopDeal->doTurn();
	}
}


void CvGame::doHolyCity()
{
	OBSERVER_PERFORMANCE("CvGame::doHolyCity");
	PlayerTypes eBestPlayer;
	TeamTypes eBestTeam;
	long lResult;
	int iValue;
	int iBestValue;
	int iI, iJ, iK;

	lResult = 0;
	gDLL->getPythonIFace()->callFunction(PYGameModule, "doHolyCity", NULL, &lResult);
	if (lResult == 1)
	{
		return;
	}

	if (getElapsedGameTurns() < 5 && !isOption(GAMEOPTION_ADVANCED_START))
	{
		return;
	}

	int iRandOffset = getSorenRandNum(GC.getNumReligionInfos(), "Holy City religion offset");
	for (int iLoop = 0; iLoop < GC.getNumReligionInfos(); ++iLoop)
	{
		iI = ((iLoop + iRandOffset) % GC.getNumReligionInfos());

		if (!isReligionSlotTaken((ReligionTypes)iI))
		{
			iBestValue = MAX_INT;
			eBestTeam = NO_TEAM;

			for (iJ = 0; iJ < MAX_TEAMS; iJ++)
			{
				if (GET_TEAM((TeamTypes)iJ).isAlive())
				{
					if (GET_TEAM((TeamTypes)iJ).isHasTech((TechTypes)(GC.getReligionInfo((ReligionTypes)iI).getTechPrereq())))
					{
						if (GET_TEAM((TeamTypes)iJ).getNumCities() > 0)
						{
							iValue = getSorenRandNum(10, "Found Religion (Team)");

							for (iK = 0; iK < GC.getNumReligionInfos(); iK++)
							{
								int iReligionCount = GET_TEAM((TeamTypes)iJ).getHasReligionCount((ReligionTypes)iK);

								if (iReligionCount > 0)
								{
									iValue += iReligionCount * 20;
								}
							}

							if (iValue < iBestValue)
							{
								iBestValue = iValue;
								eBestTeam = ((TeamTypes)iJ);
							}
						}
					}
				}
			}

			if (eBestTeam != NO_TEAM)
			{
				iBestValue = MAX_INT;
				eBestPlayer = NO_PLAYER;

				for (iJ = 0; iJ < MAX_PLAYERS; iJ++)
				{
					if (GET_PLAYER((PlayerTypes)iJ).isAlive())
					{
						if (GET_PLAYER((PlayerTypes)iJ).getTeam() == eBestTeam)
						{
							if (GET_PLAYER((PlayerTypes)iJ).getNumCities() > 0)
							{
								iValue = getSorenRandNum(10, "Found Religion (Player)");

								if (!(GET_PLAYER((PlayerTypes)iJ).isHuman()))
								{
									iValue += 10;
								}

								for (iK = 0; iK < GC.getNumReligionInfos(); iK++)
								{
									int iReligionCount = GET_PLAYER((PlayerTypes)iJ).getHasReligionCount((ReligionTypes)iK);

									if (iReligionCount > 0)
									{
										iValue += iReligionCount * 20;
									}
								}

								if (iValue < iBestValue)
								{
									iBestValue = iValue;
									eBestPlayer = ((PlayerTypes)iJ);
								}
							}
						}
					}
				}

				if (eBestPlayer != NO_PLAYER)
				{
					ReligionTypes eReligion = (ReligionTypes)iI;

					if (isOption(GAMEOPTION_PICK_RELIGION))
					{
						eReligion = GET_PLAYER(eBestPlayer).AI_chooseReligion();
					}

					if (NO_RELIGION != eReligion)
					{
						GET_PLAYER(eBestPlayer).foundReligion(eReligion, (ReligionTypes)iI, false);
					}
				}
			}
		}
	}
}


void CvGame::doHeadquarters()
{
	OBSERVER_PERFORMANCE("CvGame::doHeadquarters");
	long lResult = 0;
	gDLL->getPythonIFace()->callFunction(PYGameModule, "doHeadquarters", NULL, &lResult);
	if (lResult == 1)
	{
		return;
	}

	if (getElapsedGameTurns() < 5)
	{
		return;
	}

	for (int iI = 0; iI < GC.getNumCorporationInfos(); iI++)
	{
		CvCorporationInfo& kCorporation = GC.getCorporationInfo((CorporationTypes)iI);
		if (!isCorporationFounded((CorporationTypes)iI))
		{
			int iBestValue = MAX_INT;
			TeamTypes eBestTeam = NO_TEAM;

			for (int iJ = 0; iJ < MAX_TEAMS; iJ++)
			{
				CvTeam& kLoopTeam = GET_TEAM((TeamTypes)iJ);
				if (kLoopTeam.isAlive())
				{
					if (NO_TECH != kCorporation.getTechPrereq() && kLoopTeam.isHasTech((TechTypes)(kCorporation.getTechPrereq())))
					{
						if (kLoopTeam.getNumCities() > 0)
						{
							bool bHasBonus = false;
							for (int i = 0; i < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++i)
							{
								if (NO_BONUS != kCorporation.getPrereqBonus(i) && kLoopTeam.hasBonus((BonusTypes)kCorporation.getPrereqBonus(i)))
								{
									bHasBonus = true;
									break;
								}
							}

							if (bHasBonus)
							{
								int iValue = getSorenRandNum(10, "Found Corporation (Team)");

								for (int iK = 0; iK < GC.getNumCorporationInfos(); iK++)
								{
									int iCorporationCount = GET_PLAYER((PlayerTypes)iJ).getHasCorporationCount((CorporationTypes)iK);

									if (iCorporationCount > 0)
									{
										iValue += iCorporationCount * 20;
									}
								}

								if (iValue < iBestValue)
								{
									iBestValue = iValue;
									eBestTeam = ((TeamTypes)iJ);
								}
							}
						}
					}
				}
			}

			if (eBestTeam != NO_TEAM)
			{
				iBestValue = MAX_INT;
				PlayerTypes eBestPlayer = NO_PLAYER;

				for (int iJ = 0; iJ < MAX_PLAYERS; iJ++)
				{
					CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iJ);
					if (kLoopPlayer.isAlive())
					{
						if (kLoopPlayer.getTeam() == eBestTeam)
						{
							if (kLoopPlayer.getNumCities() > 0)
							{
								bool bHasBonus = false;
								for (int i = 0; i < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++i)
								{
									if (NO_BONUS != kCorporation.getPrereqBonus(i) && kLoopPlayer.hasBonus((BonusTypes)kCorporation.getPrereqBonus(i)))
									{
										bHasBonus = true;
										break;
									}
								}

								if (bHasBonus)
								{
									int iValue = getSorenRandNum(10, "Found Religion (Player)");

									if (!kLoopPlayer.isHuman())
									{
										iValue += 10;
									}

									for (int iK = 0; iK < GC.getNumCorporationInfos(); iK++)
									{
										int iCorporationCount = GET_PLAYER((PlayerTypes)iJ).getHasCorporationCount((CorporationTypes)iK);

										if (iCorporationCount > 0)
										{
											iValue += iCorporationCount * 20;
										}
									}

									if (iValue < iBestValue)
									{
										iBestValue = iValue;
										eBestPlayer = ((PlayerTypes)iJ);
									}
								}
							}
						}
					}
				}

				if (eBestPlayer != NO_PLAYER)
				{
					GET_PLAYER(eBestPlayer).foundCorporation((CorporationTypes)iI);
				}
			}
		}
	}
}


void CvGame::doDiploVote()
{
	OBSERVER_PERFORMANCE("CvGame::doDiploVote");
	doVoteResults();
	int iLoop;
	std::vector<int> aDelete;
	for (VoteSelectionData* pData = m_voteSelections.beginIter(&iLoop); pData; pData = m_voteSelections.nextIter(&iLoop))
		if (isApostolicCouncil(pData->eVoteSource) && (!isCouncilActive() || pData->iCouncilOwner != getApostolicPalace()->getOwnerINLINE())) aDelete.push_back(pData->getID());
	for (int i = 0; i < (int)aDelete.size(); ++i) deleteVoteSelection(aDelete[i]);
	doVoteSelection();
}


void CvGame::createBarbarianCities()
{
	CvPlot* pLoopPlot;
	CvPlot* pBestPlot;
//	long lResult; //Rhye (Kael)
	int iTargetCities;
	int iValue;
	int iBestValue;
	int iI;

	if (getMaxCityElimination() > 0)
	{
		return;
	}

	if (isOption(GAMEOPTION_NO_BARBARIANS))
	{
		return;
	}

	//Rhye - start
//Speed: Modified by Kael 04/19/2007
//	lResult = 0;
//	gDLL->getPythonIFace()->callFunction(PYGameModule, "createBarbarianCities", NULL, &lResult);
//	if (lResult == 1)
//	{
//		return;
//	}
//Speed: End Modify
	//Rhye - end

	if (GC.getEraInfo(getCurrentEra()).isNoBarbCities())
	{
		return;
	}

	if (GC.getHandicapInfo(getHandicapType()).getUnownedTilesPerBarbarianCity() <= 0)
	{
		return;
	}

	if (getNumCivCities() < (countCivPlayersAlive() * 2))
	{
		return;
	}

	if (getElapsedGameTurns() < (((GC.getHandicapInfo(getHandicapType()).getBarbarianCityCreationTurnsElapsed() * GC.getGameSpeedInfo(getGameSpeedType()).getBarbPercent()) / 100) / std::max(getStartEra() + 1, 1)))
	{
		return;
	}

	if (getSorenRandNum(100, "Barb City Creation") >= GC.getHandicapInfo(getHandicapType()).getBarbarianCityCreationProb())
	{
		return;
	}

	iBestValue = 0;
	pBestPlot = NULL;
	
	int iTargetCitiesMultiplier = 100;
	{
		int iTargetBarbCities = (getNumCivCities() * 5 * GC.getHandicapInfo(getHandicapType()).getBarbarianCityCreationProb()) / 100;
		int iBarbCities = GET_PLAYER(BARBARIAN_PLAYER).getNumCities();
		if (iBarbCities < iTargetBarbCities)
		{
			iTargetCitiesMultiplier += (300 * (iTargetBarbCities - iBarbCities)) / iTargetBarbCities;
		}
		
		if (isOption(GAMEOPTION_RAGING_BARBARIANS))
		{
			iTargetCitiesMultiplier *= 3;
			iTargetCitiesMultiplier /= 2;
		}
	}


	for (iI = 0; iI < GC.getMapINLINE().numPlotsINLINE(); iI++)
	{
		pLoopPlot = GC.getMapINLINE().plotByIndexINLINE(iI);

		if (!(pLoopPlot->isWater()))
		{
			if (!(pLoopPlot->isVisibleToCivTeam()))
			{
				iTargetCities = pLoopPlot->area()->getNumUnownedTiles();

				if (pLoopPlot->area()->getNumCities() == pLoopPlot->area()->getCitiesPerPlayer(BARBARIAN_PLAYER))
				{
					iTargetCities *= 3;
				}
								
				int iUnownedTilesThreshold = GC.getHandicapInfo(getHandicapType()).getUnownedTilesPerBarbarianCity();
				
				if (pLoopPlot->area()->getNumTiles() < (iUnownedTilesThreshold / 3))
				{
					iTargetCities *= iTargetCitiesMultiplier;
					iTargetCities /= 100;
				}				

				iTargetCities /= std::max(1, iUnownedTilesThreshold);

				if (pLoopPlot->area()->getCitiesPerPlayer(BARBARIAN_PLAYER) < iTargetCities)
				{
					iValue = GET_PLAYER(BARBARIAN_PLAYER).AI_foundValue(pLoopPlot->getX_INLINE(), pLoopPlot->getY_INLINE(), GC.getDefineINT("MIN_BARBARIAN_CITY_STARTING_DISTANCE"));
				
					if (iTargetCitiesMultiplier > 100)
					{
						iValue *= pLoopPlot->area()->getNumOwnedTiles();
					}

					iValue += (100 + getSorenRandNum(50, "Barb City Found"));
					iValue /= 100;

					if (iValue > iBestValue)
					{
						iBestValue = iValue;
						pBestPlot = pLoopPlot;
					}
				}
			}
		}
	}

	if (pBestPlot != NULL)
	{
		GET_PLAYER(BARBARIAN_PLAYER).found(pBestPlot->getX_INLINE(), pBestPlot->getY_INLINE());
	}
}


void CvGame::createBarbarianUnits()
{
	OBSERVER_PERFORMANCE("CvGame::createBarbarianUnits");
	CvUnit* pLoopUnit;
	CvArea* pLoopArea;
	CvPlot* pPlot;
	UnitAITypes eBarbUnitAI;
	UnitTypes eBestUnit;
	UnitTypes eLoopUnit;
	bool bAnimals;
//	long lResult; //Rhye (Kael)
	int iNeededBarbs;
	int iDivisor;
	int iValue;
	int iBestValue;
	int iLoop;
	int iI, iJ;

	if (isOption(GAMEOPTION_NO_BARBARIANS))
	{
		return;
	}

	//Rhye - start
//Speed: Modified by Kael 04/19/2007
//	lResult = 0;
//	gDLL->getPythonIFace()->callFunction(PYGameModule, "createBarbarianUnits", NULL, &lResult);
//	if (lResult == 1)
//	{
//		return;
//	}
//Speed: End Modify
	//Rhye - end

	bAnimals = false;

	if (GC.getEraInfo(getCurrentEra()).isNoBarbUnits())
	{
		bAnimals = true;
	}

	if (getNumCivCities() < ((countCivPlayersAlive() * 3) / 2) && !isOption(GAMEOPTION_ONE_CITY_CHALLENGE))
	{
		bAnimals = true;
	}

	if (getElapsedGameTurns() < ((GC.getHandicapInfo(getHandicapType()).getBarbarianCreationTurnsElapsed() * GC.getGameSpeedInfo(getGameSpeedType()).getBarbPercent()) / 100))
	{
		bAnimals = true;
	}

	if (bAnimals)
	{
		createAnimals();
	}
	else
	{
		return; //Rhye (so that it create just animals)

		for(pLoopArea = GC.getMapINLINE().firstArea(&iLoop); pLoopArea != NULL; pLoopArea = GC.getMapINLINE().nextArea(&iLoop))
		{
			if (pLoopArea->isWater())
			{
				eBarbUnitAI = UNITAI_ATTACK_SEA;
				iDivisor = GC.getHandicapInfo(getHandicapType()).getUnownedWaterTilesPerBarbarianUnit();
			}
			else
			{
				eBarbUnitAI = UNITAI_ATTACK;
				iDivisor = GC.getHandicapInfo(getHandicapType()).getUnownedTilesPerBarbarianUnit();
			}

			if (isOption(GAMEOPTION_RAGING_BARBARIANS))
			{
				iDivisor = std::max(1, (iDivisor / 2));
			}

			if (iDivisor > 0)
			{
				iNeededBarbs = ((pLoopArea->getNumUnownedTiles() / iDivisor) - pLoopArea->getUnitsPerPlayer(BARBARIAN_PLAYER)); // XXX eventually need to measure how many barbs of eBarbUnitAI we have in this area...

				if (iNeededBarbs > 0)
				{
					iNeededBarbs = ((iNeededBarbs / 4) + 1);

					for (iI = 0; iI < iNeededBarbs; iI++)
					{
						pPlot = GC.getMapINLINE().syncRandPlot((RANDPLOT_NOT_VISIBLE_TO_CIV | RANDPLOT_ADJACENT_LAND | RANDPLOT_PASSIBLE), pLoopArea->getID(), GC.getDefineINT("MIN_BARBARIAN_STARTING_DISTANCE"));

						if (pPlot != NULL)
						{
							//Rhye - start (no partially impassable terrains)
							if ((pPlot->getTerrainType() <= 3) && (pPlot->getFeatureType() >= 2) && (pPlot->getFeatureType() <= 4))
							{
							//Rhye - end
							eBestUnit = NO_UNIT;
							iBestValue = 0;

							for (iJ = 0; iJ < GC.getNumUnitClassInfos(); iJ++)
							{
								bool bValid = false;
								eLoopUnit = ((UnitTypes)(GC.getCivilizationInfo(GET_PLAYER(BARBARIAN_PLAYER).getCivilizationType()).getCivilizationUnits(iJ)));

								if (eLoopUnit != NO_UNIT)
								{
									CvUnitInfo& kUnit = GC.getUnitInfo(eLoopUnit);

									bValid = (kUnit.getCombat() > 0 && !kUnit.isOnlyDefensive());

									if (bValid)
									{
										if (pLoopArea->isWater() && kUnit.getDomainType() != DOMAIN_SEA)
										{
											bValid = false;
										}
										else if (!pLoopArea->isWater() && kUnit.getDomainType() != DOMAIN_LAND)
										{
											bValid = false;
										}
									}

									if (bValid)
									{
										if (!GET_PLAYER(BARBARIAN_PLAYER).canTrain(eLoopUnit))
										{
											bValid = false;
										}
									}

									if (bValid)
									{
										if (NO_BONUS != kUnit.getPrereqAndBonus())
										{
											if (!GET_TEAM(BARBARIAN_TEAM).isHasTech((TechTypes)GC.getBonusInfo((BonusTypes)kUnit.getPrereqAndBonus()).getTechCityTrade()))
											{
												bValid = false;
											}
										}
									}

									if (bValid)
									{
										bool bFound = false;
										bool bRequires = false;
										for (int i = 0; i < GC.getNUM_UNIT_PREREQ_OR_BONUSES(); ++i)
										{
											if (NO_BONUS != kUnit.getPrereqOrBonuses(i))
											{
												TechTypes eTech = (TechTypes)GC.getBonusInfo((BonusTypes)kUnit.getPrereqOrBonuses(i)).getTechCityTrade();
												if (NO_TECH != eTech)
												{
													bRequires = true;
													
													if (GET_TEAM(BARBARIAN_TEAM).isHasTech(eTech))
													{
														bFound = true;
														break;
													}
												}
											}
										}

										if (bRequires && !bFound)
										{
											bValid = false;
										}
									}

									if (bValid)
									{
										iValue = (1 + getSorenRandNum(1000, "Barb Unit Selection"));

										if (kUnit.getUnitAIType(eBarbUnitAI))
										{
											iValue += 200;
										}

										if (iValue > iBestValue)
										{
											eBestUnit = eLoopUnit;
											iBestValue = iValue;
										}
									}
								}
							}

							if (eBestUnit != NO_UNIT)
							{
								GET_PLAYER(BARBARIAN_PLAYER).initUnit(eBestUnit, pPlot->getX_INLINE(), pPlot->getY_INLINE(), eBarbUnitAI);
							}
							//Rhye - start
							}
							//Rhye - end
						}
					}
				}
			}
		}

		for (pLoopUnit = GET_PLAYER(BARBARIAN_PLAYER).firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = GET_PLAYER(BARBARIAN_PLAYER).nextUnit(&iLoop))
		{
			if (pLoopUnit->isAnimal() && pLoopUnit->getUnitType() != GC.getInfoTypeForString("UNIT_ICE_BEAR"))
			{
				pLoopUnit->kill(false);
				break;
			}
		}
	}
}


void CvGame::createAnimals()
{
	CvArea* pLoopArea;
	CvPlot* pPlot;
	UnitTypes eBestUnit;
	UnitTypes eLoopUnit;
	int iNeededAnimals;
	int iValue;
	int iBestValue;
	int iLoop;
	int iI, iJ;

	if (GC.getEraInfo(getCurrentEra()).isNoAnimals())
	{
		return;
	}

	if (GC.getHandicapInfo(getHandicapType()).getUnownedTilesPerGameAnimal() <= 0)
	{
		return;
	}

	if (getNumCivCities() < countCivPlayersAlive())
	{
		return;
	}

	if (getElapsedGameTurns() < 5)
	{
		return;
	}

	for(pLoopArea = GC.getMapINLINE().firstArea(&iLoop); pLoopArea != NULL; pLoopArea = GC.getMapINLINE().nextArea(&iLoop))
	{
		if (!(pLoopArea->isWater()))
		{
			iNeededAnimals = ((pLoopArea->getNumUnownedTiles() / GC.getHandicapInfo(getHandicapType()).getUnownedTilesPerGameAnimal()) - pLoopArea->getUnitsPerPlayer(BARBARIAN_PLAYER));

			if (iNeededAnimals > 0)
			{
				iNeededAnimals = ((iNeededAnimals / 5) + 1);

				for (iI = 0; iI < iNeededAnimals; iI++)
				{
					pPlot = GC.getMapINLINE().syncRandPlot((RANDPLOT_NOT_VISIBLE_TO_CIV | RANDPLOT_PASSIBLE), pLoopArea->getID(), GC.getDefineINT("MIN_ANIMAL_STARTING_DISTANCE"));

					if (pPlot != NULL)
					{
						eBestUnit = NO_UNIT;
						iBestValue = 0;

						for (iJ = 0; iJ < GC.getNumUnitClassInfos(); iJ++)
						{
							eLoopUnit = ((UnitTypes)(GC.getCivilizationInfo(GET_PLAYER(BARBARIAN_PLAYER).getCivilizationType()).getCivilizationUnits(iJ)));

							if (eLoopUnit != NO_UNIT)
							{
								if (GC.getUnitInfo(eLoopUnit).getUnitAIType(UNITAI_ANIMAL))
								{
									if ((pPlot->getFeatureType() != NO_FEATURE) ? GC.getUnitInfo(eLoopUnit).getFeatureNative(pPlot->getFeatureType()) : GC.getUnitInfo(eLoopUnit).getTerrainNative(pPlot->getTerrainType()))
									{
										iValue = (1 + getSorenRandNum(1000, "Animal Unit Selection"));

										if (iValue > iBestValue)
										{
											eBestUnit = eLoopUnit;
											iBestValue = iValue;
										}
									}
								}
							}
						}

						if (eBestUnit != NO_UNIT)
						{
							GET_PLAYER(BARBARIAN_PLAYER).initUnit(eBestUnit, pPlot->getX_INLINE(), pPlot->getY_INLINE(), UNITAI_ANIMAL);
						}
					}
				}
			}
		}
	}
}


void CvGame::updateWar()
{
	int iI, iJ;

	if (isOption(GAMEOPTION_ALWAYS_WAR))
	{
		for (iI = 0; iI < MAX_TEAMS; iI++)
		{
			CvTeam& kTeam1 = GET_TEAM((TeamTypes)iI);
			if (kTeam1.isAlive() && kTeam1.isHuman())
			{
				for (iJ = 0; iJ < MAX_TEAMS; iJ++)
				{
					CvTeam& kTeam2 = GET_TEAM((TeamTypes)iJ);
					if (kTeam2.isAlive() && !kTeam2.isHuman())
					{
						FAssert(iI != iJ);

						if (kTeam1.isHasMet((TeamTypes)iJ))
						{
							if (!kTeam1.isAtWar((TeamTypes)iJ))
							{
								kTeam1.declareWar(((TeamTypes)iJ), false, NO_WARPLAN);
							}
						}
					}
				}
			}
		}
	}
}


void CvGame::updateMoves()
{
	OBSERVER_PERFORMANCE("CvGame::updateMoves");
	CvSelectionGroup* pLoopSelectionGroup;
	int aiShuffle[MAX_PLAYERS];
	int iLoop;
	int iI;

	if (isMPOption(MPOPTION_SIMULTANEOUS_TURNS))
	{
		shuffleArray(aiShuffle, MAX_PLAYERS, getSorenRand());
	}
	else
	{
		for (iI = 0; iI < MAX_PLAYERS; iI++)
		{
			aiShuffle[iI] = iI;
		}
	}

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		CvPlayer& player = GET_PLAYER((PlayerTypes)(aiShuffle[iI]));

		if (player.isAlive())
		{
			if (player.isTurnActive())
			{
				if (!(player.isAutoMoves()))
				{
					player.AI_unitUpdate();

					if (!(player.isHuman()))
					{
						if (!(player.hasBusyUnit()) && !(player.hasReadyUnit(true)))
						{
							player.setAutoMoves(true);
						}
					}
				}

				if (player.isAutoMoves())
				{
					for(pLoopSelectionGroup = player.firstSelectionGroup(&iLoop); pLoopSelectionGroup; pLoopSelectionGroup = player.nextSelectionGroup(&iLoop))
					{
						pLoopSelectionGroup->autoMission();
					}

					if (!(player.hasBusyUnit()))
					{
						player.setAutoMoves(false);
					}
				}
			}
		}
	}
}


void CvGame::verifyCivics()
{
	int iI;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			GET_PLAYER((PlayerTypes)iI).verifyCivics();
		}
	}
}


void CvGame::updateTimers()
{
	int iI;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			GET_PLAYER((PlayerTypes)iI).updateTimers();
		}
	}
}


void CvGame::updateTurnTimer()
{
	int iI;

	// Are we using a turn timer?
	if (isMPOption(MPOPTION_TURN_TIMER))
	{
		if (getElapsedGameTurns() > 0 || !isOption(GAMEOPTION_ADVANCED_START))
		{
			// Has the turn expired?
			if (getTurnSlice() > getCutoffSlice())
			{
				for (iI = 0; iI < MAX_PLAYERS; iI++)
				{
					if (GET_PLAYER((PlayerTypes)iI).isAlive() && GET_PLAYER((PlayerTypes)iI).isTurnActive())
					{
						GET_PLAYER((PlayerTypes)iI).setEndTurn(true);

						if (!isMPOption(MPOPTION_SIMULTANEOUS_TURNS) && !isSimultaneousTeamTurns())
						{
							break;
						}
					}
				}
			}
		}
	}
}


void CvGame::testAlive()
{
	int iI;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		GET_PLAYER((PlayerTypes)iI).verifyAlive();
	}
}

bool CvGame::testVictory(VictoryTypes eVictory, TeamTypes eTeam, bool* pbEndScore) const
{
	FAssert(eVictory >= 0 && eVictory < GC.getNumVictoryInfos());
	FAssert(eTeam >=0 && eTeam < MAX_CIV_TEAMS);
	FAssert(GET_TEAM(eTeam).isAlive());

	bool bValid = isVictoryValid(eVictory);
	if (pbEndScore)
	{
		*pbEndScore = false;
	}

	if (bValid)
	{
		if (GC.getVictoryInfo(eVictory).isEndScore())
		{
			if (pbEndScore)
			{
				*pbEndScore = true;
			}

			if (getMaxTurns() == 0)
			{
				bValid = false;
			}
			else if (getElapsedGameTurns() < getMaxTurns())
			{
				bValid = false;
			}
			else
			{
				bool bFound = false;

				for (int iK = 0; iK < NUM_MAJOR_PLAYERS; iK++) //Rhye independents fix //MAX_CIV_TEAMS
				{
					if (GET_TEAM((TeamTypes)iK).isAlive())
					{
						if (iK != eTeam)
						{
							if (getTeamScore((TeamTypes)iK) >= getTeamScore(eTeam))
							{
								bFound = true;
								break;
							}
						}
					}
				}

				if (bFound)
				{
					bValid = false;
				}
			}
		}
	}

	if (bValid)
	{
		if (GC.getVictoryInfo(eVictory).isTargetScore())
		{
			if (getTargetScore() == 0)
			{
				bValid = false;
			}
			else if (getTeamScore(eTeam) < getTargetScore())
			{
				bValid = false;
			}
			else
			{
				bool bFound = false;

				for (int iK = 0; iK < MAX_CIV_TEAMS; iK++)
				{
					if (GET_TEAM((TeamTypes)iK).isAlive())
					{
						if (iK != eTeam)
						{
							if (getTeamScore((TeamTypes)iK) >= getTeamScore(eTeam))
							{
								bFound = true;
								break;
							}
						}
					}
				}

				if (bFound)
				{
					bValid = false;
				}
			}
		}
	}

	if (bValid)
	{
		if (GC.getVictoryInfo(eVictory).isConquest())
		{
			if (GET_TEAM(eTeam).getNumCities() == 0)
			{
				bValid = false;
			}
			else
			{
				bool bFound = false;

				for (int iK = 0; iK < MAX_CIV_TEAMS; iK++)
				{
					if (GET_TEAM((TeamTypes)iK).isAlive())
					{
						if (iK != eTeam && !GET_TEAM((TeamTypes)iK).isVassal(eTeam))
						{
							if (GET_TEAM((TeamTypes)iK).getNumCities() > 0)
							{
								bFound = true;
								break;
							}
						}
					}
				}

				if (bFound)
				{
					bValid = false;
				}
			}
		}
	}

	if (bValid)
	{
		if (GC.getVictoryInfo(eVictory).isDiploVote())
		{
			bool bFound = false;

			for (int iK = 0; iK < GC.getNumVoteInfos(); iK++)
			{
				if (GC.getVoteInfo((VoteTypes)iK).isVictory())
				{
					if (getVoteOutcome((VoteTypes)iK) == eTeam)
					{
						bFound = true;
						break;
					}
				}
			}

			if (!bFound)
			{
				bValid = false;
			}
		}
	}

	if (bValid)
	{
		if (getAdjustedPopulationPercent(eVictory) > 0)
		{
			if (100 * GET_TEAM(eTeam).getTotalPopulation() < getTotalPopulation() * getAdjustedPopulationPercent(eVictory))
			{
				bValid = false;
			}
		}
	}

	if (bValid)
	{
		if (getAdjustedLandPercent(eVictory) > 0)
		{
			if (100 * GET_TEAM(eTeam).getTotalLand() < GC.getMapINLINE().getLandPlots() * getAdjustedLandPercent(eVictory))
			{
				bValid = false;
			}
		}
	}

	if (bValid)
	{
		if (GC.getVictoryInfo(eVictory).getReligionPercent() > 0)
		{
			bool bFound = false;

			if (getNumCivCities() > (countCivPlayersAlive() * 2))
			{
				for (int iK = 0; iK < GC.getNumReligionInfos(); iK++)
				{
					if (GET_TEAM(eTeam).hasHolyCity((ReligionTypes)iK))
					{
						if (calculateReligionPercent((ReligionTypes)iK) >= GC.getVictoryInfo(eVictory).getReligionPercent())
						{
							bFound = true;
							break;
						}
					}

					if (bFound)
					{
						break;
					}
				}
			}

			if (!bFound)
			{
				bValid = false;
			}
		}
	}

	if (bValid)
	{
		if ((GC.getVictoryInfo(eVictory).getCityCulture() != NO_CULTURELEVEL) && (GC.getVictoryInfo(eVictory).getNumCultureCities() > 0))
		{
			int iCount = 0;

			for (int iK = 0; iK < MAX_CIV_PLAYERS; iK++)
			{
				if (GET_PLAYER((PlayerTypes)iK).isAlive())
				{
					if (GET_PLAYER((PlayerTypes)iK).getTeam() == eTeam)
					{
						int iLoop;
						for (CvCity* pLoopCity = GET_PLAYER((PlayerTypes)iK).firstCity(&iLoop); pLoopCity != NULL; pLoopCity = GET_PLAYER((PlayerTypes)iK).nextCity(&iLoop))
						{
							if (pLoopCity->getCultureLevel() >= GC.getVictoryInfo(eVictory).getCityCulture())
							{
								iCount++;
							}
						}
					}
				}
			}

			if (iCount < GC.getVictoryInfo(eVictory).getNumCultureCities())
			{
				bValid = false;
			}
		}
	}

	if (bValid)
	{
		if (GC.getVictoryInfo(eVictory).getTotalCultureRatio() > 0)
		{
			int iThreshold = ((GET_TEAM(eTeam).countTotalCulture() * 100) / GC.getVictoryInfo(eVictory).getTotalCultureRatio());

			bool bFound = false;

			for (int iK = 0; iK < MAX_CIV_TEAMS; iK++)
			{
				if (GET_TEAM((TeamTypes)iK).isAlive())
				{
					if (iK != eTeam)
					{
						if (GET_TEAM((TeamTypes)iK).countTotalCulture() > iThreshold)
						{
							bFound = true;
							break;
						}
					}
				}
			}

			if (bFound)
			{
				bValid = false;
			}
		}
	}

	if (bValid)
	{
		for (int iK = 0; iK < GC.getNumBuildingClassInfos(); iK++)
		{
			if (GC.getBuildingClassInfo((BuildingClassTypes) iK).getVictoryThreshold(eVictory) > GET_TEAM(eTeam).getBuildingClassCount((BuildingClassTypes)iK))
			{
				bValid = false;
				break;
			}
		}
	}

	if (bValid)
	{
		for (int iK = 0; iK < GC.getNumProjectInfos(); iK++)
		{
			if (GC.getProjectInfo((ProjectTypes) iK).getVictoryMinThreshold(eVictory) > GET_TEAM(eTeam).getProjectCount((ProjectTypes)iK))
			{
				bValid = false;
				break;
			}
		}
	}

	if (bValid)
	{
		long lResult = 1;
		CyArgsList argsList;
		argsList.add(eVictory);
		gDLL->getPythonIFace()->callFunction(PYGameModule, "isVictory", argsList.makeFunctionArgs(), &lResult);
		if (0 == lResult)
		{
			bValid = false;
		}
	}

	return bValid;
}

void CvGame::testVictory()
{
	bool bEndScore = false;

	if (getVictory() != NO_VICTORY)
	{
		return;
	}

	if (getGameState() == GAMESTATE_EXTENDED)
	{
		return;
	}

	updateScore();

	long lResult = 1;
	gDLL->getPythonIFace()->callFunction(PYGameModule, "isVictoryTest", NULL, &lResult);
	if (lResult == 0)
	{
		return;
	}

	std::vector<std::vector<int> > aaiWinners;

	for (int iI = 0; iI < MAX_CIV_TEAMS; iI++)
	{
		CvTeam& kLoopTeam = GET_TEAM((TeamTypes)iI);
		if (kLoopTeam.isAlive())
		{
			if (!(kLoopTeam.isMinorCiv()))
			{
				//Rhye - start (Historical victory should not be checked - it's triggered by python
				//for (int iJ = 0; iJ < GC.getNumVictoryInfos(); iJ++)
				for (int iJ = 0; iJ < GC.getNumVictoryInfos()-1; iJ++)
				//Rhye - end
				{
					if (testVictory((VictoryTypes)iJ, (TeamTypes)iI, &bEndScore))
					{
						if (kLoopTeam.getVictoryCountdown((VictoryTypes)iJ) < 0)
						{
							if (kLoopTeam.getVictoryDelay((VictoryTypes)iJ) == 0)
							{
								kLoopTeam.setVictoryCountdown((VictoryTypes)iJ, 0);
							}
						}

						//update victory countdown
						if (kLoopTeam.getVictoryCountdown((VictoryTypes)iJ) > 0)
						{
							kLoopTeam.changeVictoryCountdown((VictoryTypes)iJ, -1);
						}

						if (kLoopTeam.getVictoryCountdown((VictoryTypes)iJ) == 0)
						{
							if (getSorenRandNum(100, "Victory Success") < kLoopTeam.getLaunchSuccessRate((VictoryTypes)iJ))
							{
								std::vector<int> aWinner;
								aWinner.push_back(iI);
								aWinner.push_back(iJ);
								aaiWinners.push_back(aWinner);
							}
							else
							{
								kLoopTeam.resetVictoryProgress();
							}
						}
					}
				}
			}
		}

	}

	if (aaiWinners.size() > 0)
	{
		int iWinner = getSorenRandNum(aaiWinners.size(), "Victory tie breaker");
		setWinner(((TeamTypes)aaiWinners[iWinner][0]), ((VictoryTypes)aaiWinners[iWinner][1]));
	}

	if (getVictory() == NO_VICTORY)
	{
		if (getMaxTurns() > 0)
		{
			if (getElapsedGameTurns() >= getMaxTurns())
			{
				if (!bEndScore)
				{
					if (isObserverAutoPlay() || (getAIAutoPlay() > 0) || gDLL->GetAutorun())
					{
						setGameState(GAMESTATE_EXTENDED);
					}
					else
					{
						setGameState(GAMESTATE_OVER);
					}
				}
			}
		}
	}
}


void CvGame::processVote(const VoteTriggeredData& kData, int iChange)
{
	if (isApostolicCouncil(kData.eVoteSource))
	{
		if (iChange > 0) { processCouncilResolution(kData); setVoteOutcome(kData, NO_PLAYER_VOTE); }
		return;
	}
	CvVoteInfo& kVote = GC.getVoteInfo(kData.kVoteOption.eVote);

	changeTradeRoutes(kVote.getTradeRoutes() * iChange);
	changeFreeTradeCount(kVote.isFreeTrade() ? iChange : 0);
	changeNoNukesCount(kVote.isNoNukes() ? iChange : 0);

	for (int iI = 0; iI < GC.getNumCivicInfos(); iI++)
	{
		changeForceCivicCount((CivicTypes)iI, kVote.isForceCivic(iI) ? iChange : 0);
	}


	if (iChange > 0)
	{
		if (kVote.isOpenBorders())
		{
			for (int iTeam1 = 0; iTeam1 < MAX_CIV_PLAYERS; ++iTeam1)
			{
				CvTeam& kLoopTeam1 = GET_TEAM((TeamTypes)iTeam1);
				if (kLoopTeam1.isVotingMember(kData.eVoteSource))
				{
					for (int iTeam2 = iTeam1 + 1; iTeam2 < MAX_CIV_PLAYERS; ++iTeam2)
					{
						CvTeam& kLoopTeam2 = GET_TEAM((TeamTypes)iTeam2);
						if (kLoopTeam2.isVotingMember(kData.eVoteSource))
						{
							kLoopTeam1.signOpenBorders((TeamTypes)iTeam2);
						}
					}
				}
			}

			setVoteOutcome(kData, NO_PLAYER_VOTE);
		}
		else if (kVote.isDefensivePact())
		{
			for (int iTeam1 = 0; iTeam1 < MAX_CIV_PLAYERS; ++iTeam1)
			{
				CvTeam& kLoopTeam1 = GET_TEAM((TeamTypes)iTeam1);
				if (kLoopTeam1.isVotingMember(kData.eVoteSource))
				{
					for (int iTeam2 = iTeam1 + 1; iTeam2 < MAX_CIV_PLAYERS; ++iTeam2)
					{
						CvTeam& kLoopTeam2 = GET_TEAM((TeamTypes)iTeam2);
						if (kLoopTeam2.isVotingMember(kData.eVoteSource))
						{
							kLoopTeam1.signDefensivePact((TeamTypes)iTeam2);
						}
					}
				}
			}

			setVoteOutcome(kData, NO_PLAYER_VOTE);
		}
		else if (kVote.isForcePeace())
		{
			FAssert(NO_PLAYER != kData.kVoteOption.ePlayer);
			CvPlayer& kPlayer = GET_PLAYER(kData.kVoteOption.ePlayer);

			for (int iPlayer = 0; iPlayer < MAX_CIV_PLAYERS; ++iPlayer)
			{
				CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iPlayer);
				if (kLoopPlayer.getTeam() != kPlayer.getTeam())
				{
					if (kLoopPlayer.isVotingMember(kData.eVoteSource))
					{
						//Rhye - start
						//kLoopPlayer.forcePeace(kData.kVoteOption.ePlayer);
						if (atWar(kPlayer.getTeam(), (TeamTypes)iPlayer)) {
							kLoopPlayer.forcePeace(kData.kVoteOption.ePlayer);
						}
						//Rhye - end
					}
				}
			}

			setVoteOutcome(kData, NO_PLAYER_VOTE);
		}
		else if (kVote.isForceNoTrade())
		{
			FAssert(NO_PLAYER != kData.kVoteOption.ePlayer);
			CvPlayer& kPlayer = GET_PLAYER(kData.kVoteOption.ePlayer);

			for (int iPlayer = 0; iPlayer < MAX_CIV_PLAYERS; ++iPlayer)
			{
				CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iPlayer);
				if (kLoopPlayer.isVotingMember(kData.eVoteSource))
				{
					if (kLoopPlayer.canStopTradingWithTeam(kPlayer.getTeam()))
					{
						kLoopPlayer.stopTradingWithTeam(kPlayer.getTeam());
					}
				}
			}

			setVoteOutcome(kData, NO_PLAYER_VOTE);
		}
		else if (kVote.isForceWar())
		{
			FAssert(NO_PLAYER != kData.kVoteOption.ePlayer);
			CvPlayer& kPlayer = GET_PLAYER(kData.kVoteOption.ePlayer);

			for (int iPlayer = 0; iPlayer < MAX_CIV_PLAYERS; ++iPlayer)
			{
				CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iPlayer);
				if (kLoopPlayer.isVotingMember(kData.eVoteSource))
				{
					if (GET_TEAM(kLoopPlayer.getTeam()).canChangeWarPeace(kPlayer.getTeam()))
					{
						GET_TEAM(kLoopPlayer.getTeam()).declareWar(kPlayer.getTeam(), false, WARPLAN_DOGPILE);
					}
				}
			}

			setVoteOutcome(kData, NO_PLAYER_VOTE);
		}
		else if (kVote.isAssignCity())
		{
			FAssert(NO_PLAYER != kData.kVoteOption.ePlayer);
			CvPlayer& kPlayer = GET_PLAYER(kData.kVoteOption.ePlayer);
			CvCity* pCity = kPlayer.getCity(kData.kVoteOption.iCityId);
			FAssert(NULL != pCity);

			if (NULL != pCity)
			{
				if (NO_PLAYER != kData.kVoteOption.eOtherPlayer && kData.kVoteOption.eOtherPlayer != pCity->getOwnerINLINE())
				{
					GET_PLAYER(kData.kVoteOption.eOtherPlayer).acquireCity(pCity, false, true, true);
				}
			}

			setVoteOutcome(kData, NO_PLAYER_VOTE);
		}
	}
}


int CvGame::getIndexAfterLastDeal()
{
	return m_deals.getIndexAfterLast();
}


int CvGame::getNumDeals()
{
	return m_deals.getCount();
}


 CvDeal* CvGame::getDeal(int iID)																		
{
	return ((CvDeal *)(m_deals.getAt(iID)));
}


CvDeal* CvGame::addDeal()
{
	return ((CvDeal *)(m_deals.add()));
}


 void CvGame::deleteDeal(int iID)
{
	m_deals.removeAt(iID);
	gDLL->getInterfaceIFace()->setDirty(Foreign_Screen_DIRTY_BIT, true);
}

CvDeal* CvGame::firstDeal(int *pIterIdx, bool bRev)
{
	return !bRev ? m_deals.beginIter(pIterIdx) : m_deals.endIter(pIterIdx);
}


CvDeal* CvGame::nextDeal(int *pIterIdx, bool bRev)
{
	return !bRev ? m_deals.nextIter(pIterIdx) : m_deals.prevIter(pIterIdx);
}


 CvRandom& CvGame::getMapRand()																					
{
	return m_mapRand;
}


int CvGame::getMapRandNum(int iNum, const char* pszLog)
{
	return m_mapRand.get(iNum, pszLog);
}


CvRandom& CvGame::getSorenRand()																					
{
	return m_sorenRand;
}


int CvGame::getSorenRandNum(int iNum, const char* pszLog)
{
	return m_sorenRand.get(iNum, pszLog);
	//RFCMP
	//return (GC.getGameINLINE().getSorenRand().getSeed() + GC.getGameINLINE().getGameTurn()) % iNum;
}


int CvGame::calculateSyncChecksum()
{
	PROFILE_FUNC();

	CvUnit* pLoopUnit;
	int iMultiplier;
	int iValue;
	int iLoop;
	int iI, iJ;

	iValue = 0;

	iValue += getMapRand().getSeed();
	iValue += getSorenRand().getSeed();
    for (int iEmbargoTeam = 0; iEmbargoTeam < MAX_TEAMS; iEmbargoTeam++)
        for (int iEmbargoTarget = 0; iEmbargoTarget < MAX_TEAMS; iEmbargoTarget++)
            if (GET_TEAM((TeamTypes)iEmbargoTeam).isTradeEmbargo((TeamTypes)iEmbargoTarget))
                iValue += (iEmbargoTeam + 1) * (iEmbargoTarget + 1) * 7919;

    for (int iFoodPlayer = 0; iFoodPlayer < MAX_PLAYERS; ++iFoodPlayer)
    {
        int iFoodLoop;
        for (CvCity* pFoodCity = GET_PLAYER((PlayerTypes)iFoodPlayer).firstCity(&iFoodLoop); pFoodCity != NULL;
            pFoodCity = GET_PLAYER((PlayerTypes)iFoodPlayer).nextCity(&iFoodLoop))
            iValue += (pFoodCity->getFoodTradeChecksum() + pFoodCity->getGrowthFoodRemainder() * 101) *
                (iFoodPlayer + 1) * (pFoodCity->getID() + 1);
    }
	iValue += (m_iPapalPlayer + 1) * 269 + m_iPapalRetryTurn * 271 + m_iPapalDecisionSerial * 277 + m_bPapalPalaceEffects * 281;
	for (int iBirth = 0; iBirth < MAX_CIV_PLAYERS; ++iBirth)
		iValue += (GET_PLAYER((PlayerTypes)iBirth).getLastBirthTurn() + 1) * (iBirth + 1) * 317;
	iValue += (m_iPapalRefuser + 1) * 283;
	iValue += (m_iPapalFirstCouncilTurn + 1) * 313;
	iValue += (m_iPapalRomeDeadline + 1) * 307 + (m_iPapalDevotionFadeStart + 1) * 311;
	for (int iRefusal = 0; iRefusal < MAX_CIV_PLAYERS; ++iRefusal) iValue += m_aiPapalRefusalPenalties[iRefusal] * (iRefusal + 1) * 293;
	for (std::map<int, PlayerTypes>::const_iterator p = m_papalDecisions.begin(); p != m_papalDecisions.end(); ++p) iValue += (p->first + 1) * (p->second + 1) * 283;
	iValue += (m_iCrusadeRegion + 1) * 7919 + m_iCrusadeEndTurn * 101;
	for (int t = 0; t < MAX_TEAMS; ++t) iValue += (t + 1) * (m_abCrusadeParticipants[t] * 241 + m_abCrusadeTargets[t] * 251);
	for (int i = 0; i < MAX_PLAYERS; ++i) iValue += (i + 1) * (m_aiCrusadePlunder[i] * 257 + m_abCrusadeHolyStates[i] * 263);
	for (int iReward = 0; iReward < MAX_CIV_PLAYERS; ++iReward) iValue += (iReward + 1) * (m_aiCrusadeRewards[iReward] + 1) * 131;
	int iCouncilLoop;
	for (VoteTriggeredData* pCouncil = m_votesTriggered.beginIter(&iCouncilLoop); pCouncil; pCouncil = m_votesTriggered.nextIter(&iCouncilLoop))
	{
		if (!isApostolicCouncil(pCouncil->eVoteSource)) continue;
		iValue += pCouncil->getID() * 197 + pCouncil->iCouncilDeadline * 211 + pCouncil->kVoteOption.eVote * 223;
		for (int iVoter = 0; iVoter < MAX_CIV_PLAYERS; ++iVoter)
			iValue += (iVoter + 1) * (pCouncil->aiCouncilWeight[iVoter] * 227 + pCouncil->aiCouncilDelivery[iVoter] * 229 + (getPlayerVote((PlayerTypes)iVoter, pCouncil->getID()) + 10) * 233);
	}
	iValue += getNumCities();
	iValue += getTotalPopulation();
	iValue += getNumDeals();

	iValue += GC.getMapINLINE().getOwnedPlots();
	iValue += GC.getMapINLINE().getNumAreas();

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isEverAlive())
		{
			iMultiplier = getPlayerScore((PlayerTypes)iI);

			switch (getTurnSlice() % 4)
			{
			case 0:
				iMultiplier += (GET_PLAYER((PlayerTypes)iI).getTotalPopulation() * 543271);
				iMultiplier += (GET_PLAYER((PlayerTypes)iI).getTotalLand() * 327382);
				iMultiplier += (GET_PLAYER((PlayerTypes)iI).getGold() * 107564);
				iMultiplier += (GET_PLAYER((PlayerTypes)iI).getAssets() * 327455);
				iMultiplier += (GET_PLAYER((PlayerTypes)iI).getPower() * 135647);
				iMultiplier += (GET_PLAYER((PlayerTypes)iI).getNumCities() * 436432);
				iMultiplier += (GET_PLAYER((PlayerTypes)iI).getNumUnits() * 324111);
				iMultiplier += (GET_PLAYER((PlayerTypes)iI).getNumSelectionGroups() * 215356);
				break;

			case 1:
				for (iJ = 0; iJ < NUM_YIELD_TYPES; iJ++)
				{
					iMultiplier += (GET_PLAYER((PlayerTypes)iI).calculateTotalYield((YieldTypes)iJ) * 432754);
				}

				for (iJ = 0; iJ < NUM_COMMERCE_TYPES; iJ++)
				{
					iMultiplier += (GET_PLAYER((PlayerTypes)iI).getCommerceRate((CommerceTypes)iJ) * 432789);
				}
				break;

			case 2:
				for (iJ = 0; iJ < GC.getNumBonusInfos(); iJ++)
				{
					iMultiplier += (GET_PLAYER((PlayerTypes)iI).getNumAvailableBonuses((BonusTypes)iJ) * 945732);
					iMultiplier += (GET_PLAYER((PlayerTypes)iI).getBonusImport((BonusTypes)iJ) * 326443);
					iMultiplier += (GET_PLAYER((PlayerTypes)iI).getBonusExport((BonusTypes)iJ) * 932211);
				}

				for (iJ = 0; iJ < GC.getNumImprovementInfos(); iJ++)
				{
					iMultiplier += (GET_PLAYER((PlayerTypes)iI).getImprovementCount((ImprovementTypes)iJ) * 883422);
				}

				for (iJ = 0; iJ < GC.getNumBuildingClassInfos(); iJ++)
				{
					iMultiplier += (GET_PLAYER((PlayerTypes)iI).getBuildingClassCountPlusMaking((BuildingClassTypes)iJ) * 954531);
				}

				for (iJ = 0; iJ < GC.getNumUnitClassInfos(); iJ++)
				{
					iMultiplier += (GET_PLAYER((PlayerTypes)iI).getUnitClassCountPlusMaking((UnitClassTypes)iJ) * 754843);
				}

				for (iJ = 0; iJ < NUM_UNITAI_TYPES; iJ++)
				{
					iMultiplier += (GET_PLAYER((PlayerTypes)iI).AI_totalUnitAIs((UnitAITypes)iJ) * 643383);
				}
				break;

			case 3:
				for (pLoopUnit = GET_PLAYER((PlayerTypes)iI).firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = GET_PLAYER((PlayerTypes)iI).nextUnit(&iLoop))
				{
					iMultiplier += (pLoopUnit->getX_INLINE() * 876543);
					iMultiplier += (pLoopUnit->getY_INLINE() * 985310);
					iMultiplier += (pLoopUnit->getDamage() * 736373);
					iMultiplier += (pLoopUnit->getExperience() * 820622);
					iMultiplier += (pLoopUnit->getLevel() * 367291);
				}
				break;
			}

			if (iMultiplier != 0)
			{
				iValue *= iMultiplier;
			}
		}
	}

	return iValue;
}


int CvGame::calculateOptionsChecksum()
{
	PROFILE_FUNC();

	int iValue;
	int iI, iJ;

	iValue = 0;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		for (iJ = 0; iJ < NUM_PLAYEROPTION_TYPES; iJ++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isOption((PlayerOptionTypes)iJ))
			{
				iValue += (iI * 943097);
				iValue += (iJ * 281541);
			}
		}
	}

	return iValue;
}


//Rhye - start (jdog) for Warlords
// Return success of changing properties of player
// playerIdx is index of player to be changed ... must have been alive at some point (otherwise use createNewPlayer)
// newCivType is index of new civ
// newLeader is index of new leader of that civ, currently has to be for the civ
// teamIdx is team civ should join, -1 for no change
// bIsHuman, true if player is to be human controlled
// bChangeGraphics, true to update player graphics to new civ type (leader head graphics always change)
bool CvGame::changePlayer( int playerIdx, int newCivType, int newLeader, int teamIdx, bool bIsHuman, bool bChangeGraphics )
{
	bool changedCivOrLeader = false;
	LeaderHeadTypes prevLeader = NO_LEADER;
	CvFlagEntity* newFlagSymbol = NULL;
	CvUnit* pLoopUnit;
	CvUnit* pNewUnit;
	int iLoop;
	TeamTypes prevTeam = GET_PLAYER((PlayerTypes)playerIdx).getTeam();

	if( playerIdx >= GC.getMAX_CIV_PLAYERS() )
	{
		//logMsg("Creating new player ... failed, invalid player index");
		return false;
	}
	if( !GET_PLAYER((PlayerTypes)playerIdx).isEverAlive() )
	{
		//logMsg("Changing player ... failed, player id never alive");
		return false;
	}
	if( newCivType >= GC.getNumCivilizationInfos() )
	{
		//logMsg("Creating new player ... failed, invalid civ type");
		return false;
	}
	if( newLeader >= GC.getNumLeaderHeadInfos() )
	{
		//logMsg("Creating new player ... failed, invalid leader type");
		return false;
	}
	if( teamIdx >= GC.getMAX_TEAMS() ) //( teamIdx >= GC.getMAX_CIV_TEAMS() )
	{
		//logMsg("Creating new player ... failed, invalid team index");
		return false;
	}

	//logMsg("Changing player ...");

	// Change whether this player is human
	if( bIsHuman )
	{
		if( GC.getInitCore().getSlotStatus( (PlayerTypes)playerIdx ) != SS_TAKEN )
			GC.getInitCore().setSlotStatus( (PlayerTypes)playerIdx, SS_TAKEN );
	}
	else
	{
		if( GC.getInitCore().getSlotStatus( (PlayerTypes)playerIdx ) == SS_TAKEN )
			GC.getInitCore().setSlotStatus( (PlayerTypes)playerIdx, SS_COMPUTER ); // or SS_OPEN?
	}
	
	// Change civ type
	if( (CivilizationTypes)newCivType != GC.getInitCore().getCiv((PlayerTypes)playerIdx) )
	{
		//logMsg("Changing civType");

		GC.getInitCore().setCiv((PlayerTypes)playerIdx, (CivilizationTypes)newCivType);

		changedCivOrLeader = true;
	}
	
	// Change Leader Head
	if( (LeaderHeadTypes)newLeader != GC.getInitCore().getLeader((PlayerTypes)playerIdx ) )
	{
		//logMsg("Changeing Leader");
		prevLeader = GC.getInitCore().getLeader((PlayerTypes)playerIdx );

		if( !GC.getCivilizationInfo( (CivilizationTypes)newCivType ).isLeaders( (LeaderHeadTypes)newLeader) )
		{
			//logMsg("WARNING: New leader not for this civ");
		}

		GC.getInitCore().setLeader((PlayerTypes)playerIdx, (LeaderHeadTypes)newLeader );
		GC.getInitCore().setLeaderName((PlayerTypes)playerIdx, GC.getLeaderHeadInfo((LeaderHeadTypes)newLeader).getDescription(0)); //Rhye

		changedCivOrLeader = true;
	}

	// Place on a different team?
	if( teamIdx >= 0 && (TeamTypes)teamIdx != prevTeam )
	{
		if( GET_TEAM(prevTeam).getNumMembers() == 1 ) 
		{
			GET_TEAM( (TeamTypes)teamIdx ).addTeam(prevTeam);
			gDLL->getInterfaceIFace()->setDirty(Fog_DIRTY_BIT, true);
			gDLL->getEngineIFace()->SetDirty(MinimapTexture_DIRTY_BIT, true);
			gDLL->getEngineIFace()->SetDirty(GlobeTexture_DIRTY_BIT, true);
			gDLL->getEngineIFace()->SetDirty(GlobePartialTexture_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(GlobeLayer_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(Score_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(Foreign_Screen_DIRTY_BIT, true);
		}
		else
		{
			// This handles both changes to prev team and new team
			GET_PLAYER((PlayerTypes)playerIdx).setTeam((TeamTypes)teamIdx);
			gDLL->getInterfaceIFace()->setDirty(Fog_DIRTY_BIT, true);
			gDLL->getEngineIFace()->SetDirty(MinimapTexture_DIRTY_BIT, true);
			gDLL->getEngineIFace()->SetDirty(GlobeTexture_DIRTY_BIT, true);
			gDLL->getEngineIFace()->SetDirty(GlobePartialTexture_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(GlobeLayer_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(Score_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(Foreign_Screen_DIRTY_BIT, true);
		}
	}

	// Update civs colors, artstyle, border colors, leader name on the score board, etc.
	// Current challenge is getting existing units to change their flag ... 
	if( bChangeGraphics )
	{
		//logMsg("Changing player graphics");
		CivilizationTypes civType = GET_PLAYER((PlayerTypes)playerIdx).getCivilizationType();
		GC.getInitCore().setFlagDecal( (PlayerTypes)playerIdx, (CvWString)GC.getCivilizationInfo(civType).getFlagTexture() );
		// Successor banners can use full-color art rather than a team-color mask.
		GC.getInitCore().setWhiteFlag( (PlayerTypes)playerIdx, GC.getCivilizationInfo(civType).getArtInfo()->isWhiteFlag() );
		GC.getInitCore().setColor( (PlayerTypes)playerIdx, (PlayerColorTypes)GC.getCivilizationInfo(civType).getDefaultPlayerColor() );
		GC.getInitCore().setArtStyle( (PlayerTypes)playerIdx, (ArtStyleTypes)GC.getCivilizationInfo(civType).getArtStyleType() );

		// Need to force redraw
		gDLL->getEngineIFace()->SetDirty(CultureBorders_DIRTY_BIT, true);
		gDLL->getEngineIFace()->SetDirty(MinimapTexture_DIRTY_BIT, true);
		gDLL->getEngineIFace()->SetDirty(GlobeTexture_DIRTY_BIT, true);
		gDLL->getEngineIFace()->SetDirty(GlobePartialTexture_DIRTY_BIT, true);

		gDLL->getInterfaceIFace()->setDirty(ColoredPlots_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(HighlightPlot_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(CityInfo_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(UnitInfo_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(InfoPane_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(GlobeLayer_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(Flag_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(MinimapSection_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(Score_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(Foreign_Screen_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(SelectionSound_DIRTY_BIT, true);
		gDLL->getInterfaceIFace()->setDirty(GlobeInfo_DIRTY_BIT, true);
/*
		//Change existing unit flags
		newFlagSymbol = gDLL->getFlagEntityIFace()->create((PlayerTypes)playerIdx);
		if( newFlagSymbol != NULL )
		{
			for(pLoopUnit = GET_PLAYER((PlayerTypes)playerIdx).firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = GET_PLAYER((PlayerTypes)playerIdx).nextUnit(&iLoop))
			{
				pLoopPlot = GC.getMapINLINE().plotINLINE(pLoopUnit->getX(),pLoopUnit->getY());
				//pLoopPlot->updateFlagSymbol();
				//gDLL->getFlagEntityIFace()->updateUnitInfo(newFlagSymbol, pLoopPlot);
			}
		}
		else 
		{
			logMsg("New flag creation failed.");
		}
*/
		
		int numUnits = GET_PLAYER((PlayerTypes)playerIdx).getNumUnits();
		int i = 0;

		// Loop through players units, converting them
		for (pLoopUnit = GET_PLAYER((PlayerTypes)playerIdx).firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = GET_PLAYER((PlayerTypes)playerIdx).nextUnit(&iLoop))
		{
			// Concept borrowed from CvUnit::gift
			pNewUnit = GET_PLAYER((PlayerTypes)playerIdx).initUnit(pLoopUnit->getUnitType(), pLoopUnit->getX_INLINE(), pLoopUnit->getY_INLINE(), pLoopUnit->AI_getUnitAIType());
			// Will kill pLoopUnit
			pNewUnit->convert(pLoopUnit);

			char cArray[99];
			sprintf(cArray, "Converting unit type: %d", pNewUnit->getUnitType());
			//logMsg(cArray);

			// Without this, is infinite loop ...
			i++;
			if( i >= numUnits )
				break;
		}

	}

	// If civ or leader changed, need to update traits/personality/civ data
	if( changedCivOrLeader )
	{
		GET_PLAYER((PlayerTypes)playerIdx).reinit((PlayerTypes)playerIdx, prevLeader, false);
	}

	//logMsg("Player change complete");

	return true;
}

void CvGame::convertUnits( int playerIdx )
{
	CvUnit* pLoopUnit;
	CvUnit* pNewUnit;
	int iLoop;
	int numUnits = GET_PLAYER((PlayerTypes)playerIdx).getNumUnits();
	int i = 0;

	// Loop through players units, converting them
	for (pLoopUnit = GET_PLAYER((PlayerTypes)playerIdx).firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = GET_PLAYER((PlayerTypes)playerIdx).nextUnit(&iLoop))
	{
		// Concept borrowed from CvUnit::gift
		pNewUnit = GET_PLAYER((PlayerTypes)playerIdx).initUnit(pLoopUnit->getUnitType(), pLoopUnit->getX_INLINE(), pLoopUnit->getY_INLINE(), pLoopUnit->AI_getUnitAIType());
		// Will kill pLoopUnit
		pNewUnit->convert(pLoopUnit);

		char cArray[99];
		sprintf(cArray, "Converting unit type: %d", pNewUnit->getUnitType());
		//logMsg(cArray);

		// Without this, is infinite loop ...
		i++;
		if( i >= numUnits )
			break;
	}
}
// Rhye - end (jdog)



void CvGame::addReplayMessage(ReplayMessageTypes eType, PlayerTypes ePlayer, CvWString pszText, int iPlotX, int iPlotY, ColorTypes eColor)
{
	int iGameTurn = getGameTurn();
	CvReplayMessage* pMessage = new CvReplayMessage(iGameTurn, eType, ePlayer);
	if (NULL != pMessage)
	{
		pMessage->setPlot(iPlotX, iPlotY);
		pMessage->setText(pszText);
		if (NO_COLOR == eColor)
		{
			eColor = (ColorTypes)GC.getInfoTypeForString("COLOR_WHITE");
		}
		pMessage->setColor(eColor);
		m_listReplayMessages.push_back(pMessage);
	}
}

void CvGame::clearReplayMessageMap()
{
	for (ReplayMessageList::const_iterator itList = m_listReplayMessages.begin(); itList != m_listReplayMessages.end(); itList++)
	{
		const CvReplayMessage* pMessage = *itList;
		if (NULL != pMessage)
		{
			delete pMessage;
		}
	}
	m_listReplayMessages.clear();
}

int CvGame::getReplayMessageTurn(uint i) const
{
	if (i >= m_listReplayMessages.size())
	{
		return (-1);
	}
	const CvReplayMessage* pMessage =  m_listReplayMessages[i];
	if (NULL == pMessage)
	{
		return (-1);
	}
	return pMessage->getTurn();
}

ReplayMessageTypes CvGame::getReplayMessageType(uint i) const
{
	if (i >= m_listReplayMessages.size())
	{
		return (NO_REPLAY_MESSAGE);
	}
	const CvReplayMessage* pMessage =  m_listReplayMessages[i];
	if (NULL == pMessage)
	{
		return (NO_REPLAY_MESSAGE);
	}
	return pMessage->getType();
}

int CvGame::getReplayMessagePlotX(uint i) const
{
	if (i >= m_listReplayMessages.size())
	{
		return (-1);
	}
	const CvReplayMessage* pMessage =  m_listReplayMessages[i];
	if (NULL == pMessage)
	{
		return (-1);
	}
	return pMessage->getPlotX();
}

int CvGame::getReplayMessagePlotY(uint i) const
{
	if (i >= m_listReplayMessages.size())
	{
		return (-1);
	}
	const CvReplayMessage* pMessage =  m_listReplayMessages[i];
	if (NULL == pMessage)
	{
		return (-1);
	}
	return pMessage->getPlotY();
}

PlayerTypes CvGame::getReplayMessagePlayer(uint i) const
{
	if (i >= m_listReplayMessages.size())
	{
		return (NO_PLAYER);
	}
	const CvReplayMessage* pMessage =  m_listReplayMessages[i];
	if (NULL == pMessage)
	{
		return (NO_PLAYER);
	}
	return pMessage->getPlayer();
}

LPCWSTR CvGame::getReplayMessageText(uint i) const
{
	if (i >= m_listReplayMessages.size())
	{
		return (NULL);
	}
	const CvReplayMessage* pMessage =  m_listReplayMessages[i];
	if (NULL == pMessage)
	{
		return (NULL);
	}
	return pMessage->getText().GetCString();
}

ColorTypes CvGame::getReplayMessageColor(uint i) const
{
	if (i >= m_listReplayMessages.size())
	{
		return (NO_COLOR);
	}
	const CvReplayMessage* pMessage =  m_listReplayMessages[i];
	if (NULL == pMessage)
	{
		return (NO_COLOR);
	}
	return pMessage->getColor();
}


uint CvGame::getNumReplayMessages() const
{
	return m_listReplayMessages.size();
}

// Private Functions...

void CvGame::read(FDataStreamBase* pStream)
{
	int iI;

	reset(NO_HANDICAP);

	uint uiFlag=0;
	pStream->Read(&uiFlag);	// flags for expansion

	if (uiFlag < 1)
	{
		int iEndTurnMessagesSent;
		pStream->Read(&iEndTurnMessagesSent);
	}
	pStream->Read(&m_iElapsedGameTurns);
	pStream->Read(&m_iStartTurn);
	pStream->Read(&m_iStartYear);
	pStream->Read(&m_iEstimateEndTurn);
	pStream->Read(&m_iTurnSlice);
	pStream->Read(&m_iCutoffSlice);
	pStream->Read(&m_iNumGameTurnActive);
	pStream->Read(&m_iNumCities);
	pStream->Read(&m_iTotalPopulation);
	pStream->Read(&m_iTradeRoutes);
	pStream->Read(&m_iFreeTradeCount);
	pStream->Read(&m_iNoNukesCount);
	pStream->Read(&m_iNukesExploded);
	pStream->Read(&m_iMaxPopulation);
	pStream->Read(&m_iMaxLand);
	pStream->Read(&m_iMaxTech);
	pStream->Read(&m_iMaxWonders);
	pStream->Read(&m_iInitPopulation);
	pStream->Read(&m_iInitLand);
	pStream->Read(&m_iInitTech);
	pStream->Read(&m_iInitWonders);
	pStream->Read(&m_iAIAutoPlay);
	pStream->Read(&m_iCircumnavigated); //Rhye

	// m_uiInitialTime not saved

	pStream->Read(&m_bScoreDirty);
	pStream->Read(&m_bCircumnavigated);
	// m_bDebugMode not saved
	pStream->Read(&m_bFinalInitialized);
	// m_bPbemTurnSent not saved
	pStream->Read(&m_bHotPbemBetweenTurns);
	// m_bPlayerOptionsSent not saved
	pStream->Read(&m_bNukesValid);

	pStream->Read((int*)&m_eHandicap);
	pStream->Read((int*)&m_ePausePlayer);
	pStream->Read((int*)&m_eBestLandUnit);
	pStream->Read((int*)&m_eWinner);
	pStream->Read((int*)&m_eVictory);
	pStream->Read((int*)&m_eGameState);

	//Rhye - start bugfix (thanks Gyathaar)
	//pStream->ReadString(m_szScriptData);
	int charcount;
	char letter;
	pStream->Read(&charcount);
	m_szScriptData = "";
	for (iI=0;iI<charcount;iI++)
	{
		pStream->Read(&letter);
		m_szScriptData += letter;
	} 
	//Rhye - end

	if (uiFlag < 1)
	{
		std::vector<int> aiEndTurnMessagesReceived(MAX_PLAYERS);
		pStream->Read(MAX_PLAYERS, &aiEndTurnMessagesReceived[0]);
	}
	pStream->Read(MAX_PLAYERS, m_aiRankPlayer);
	pStream->Read(MAX_PLAYERS, m_aiPlayerRank);
	pStream->Read(MAX_PLAYERS, m_aiPlayerScore);
	pStream->Read(MAX_TEAMS, m_aiRankTeam);
	pStream->Read(MAX_TEAMS, m_aiTeamRank);
	pStream->Read(MAX_TEAMS, m_aiTeamScore);

	pStream->Read(GC.getNumUnitInfos(), m_paiUnitCreatedCount);
	pStream->Read(GC.getNumUnitClassInfos(), m_paiUnitClassCreatedCount);
	pStream->Read(GC.getNumBuildingClassInfos(), m_paiBuildingClassCreatedCount);
	pStream->Read(GC.getNumProjectInfos(), m_paiProjectCreatedCount);
	pStream->Read(GC.getNumCivicInfos(), m_paiForceCivicCount);
	pStream->Read(GC.getNumVoteInfos(), (int*)m_paiVoteOutcome);
	pStream->Read(GC.getNumReligionInfos(), m_paiReligionGameTurnFounded);
	pStream->Read(GC.getNumCorporationInfos(), m_paiCorporationGameTurnFounded);
	pStream->Read(GC.getNumVoteSourceInfos(), m_aiSecretaryGeneralTimer);
	pStream->Read(GC.getNumVoteSourceInfos(), m_aiVoteTimer);
	pStream->Read(GC.getNumVoteSourceInfos(), m_aiDiploVote);

	pStream->Read(GC.getNumSpecialUnitInfos(), m_pabSpecialUnitValid);
	pStream->Read(GC.getNumSpecialBuildingInfos(), m_pabSpecialBuildingValid);
	pStream->Read(GC.getNumReligionInfos(), m_abReligionSlotTaken);

	for (iI=0;iI<GC.getNumReligionInfos();iI++)
	{
		pStream->Read((int*)&m_paHolyCity[iI].eOwner);
		pStream->Read(&m_paHolyCity[iI].iID);
	}

	for (iI=0;iI<GC.getNumCorporationInfos();iI++)
	{
		pStream->Read((int*)&m_paHeadquarters[iI].eOwner);
		pStream->Read(&m_paHeadquarters[iI].iID);
	}

	{
		CvWString szBuffer;
		uint iSize;

		m_aszDestroyedCities.clear();
		pStream->Read(&iSize);
		for (uint i = 0; i < iSize; i++)
		{
			pStream->ReadString(szBuffer);
			m_aszDestroyedCities.push_back(szBuffer);
		}

		m_aszGreatPeopleBorn.clear();
		pStream->Read(&iSize);
		for (uint i = 0; i < iSize; i++)
		{
			pStream->ReadString(szBuffer);
			m_aszGreatPeopleBorn.push_back(szBuffer);
		}
	}

	ReadStreamableFFreeListTrashArray(m_deals, pStream);
	ReadStreamableFFreeListTrashArray(m_voteSelections, pStream);
	ReadStreamableFFreeListTrashArray(m_votesTriggered, pStream);
	pStream->Read(&m_iCrusadeRegion);
	pStream->Read(MAX_TEAMS, m_abCrusadeParticipants);
	pStream->Read(MAX_TEAMS, m_abCrusadeTargets);
	pStream->Read(MAX_PLAYERS, m_aiCrusadePlunder);
	pStream->Read(MAX_PLAYERS, m_abCrusadeHolyStates);
	pStream->Read(&m_iPapalPlayer);
	pStream->Read(&m_iPapalRetryTurn);
	pStream->Read(&m_iPapalFirstCouncilTurn);
	pStream->Read(&m_iPapalRomeDeadline);
	pStream->Read(&m_iPapalDevotionFadeStart);
	pStream->Read(&m_iPapalDecisionSerial);
	pStream->Read(&m_iPapalRefuser);
	pStream->Read(MAX_CIV_PLAYERS, m_aiPapalRefusalPenalties);
	pStream->Read(&m_bPapalPalaceEffects);
	int iPapalPending;
	pStream->Read(&iPapalPending);
	m_papalDecisions.clear();
	for (int p = 0; p < iPapalPending; ++p)
	{
		int iId, iOwner; pStream->Read(&iId); pStream->Read(&iOwner);
		m_papalDecisions[iId] = (PlayerTypes)iOwner;
	}
	pStream->Read(&m_iCrusadeEndTurn);
	pStream->Read(MAX_CIV_PLAYERS, m_aiCrusadeRewards);

	m_mapRand.read(pStream);
	m_sorenRand.read(pStream);

	{
		clearReplayMessageMap();
		ReplayMessageList::size_type iSize;
		pStream->Read(&iSize);
		for (ReplayMessageList::size_type i = 0; i < iSize; i++)
		{
			CvReplayMessage* pMessage = new CvReplayMessage(0);
			if (NULL != pMessage)
			{
				pMessage->read(*pStream);
			}
			m_listReplayMessages.push_back(pMessage);
		}
	}
	// m_pReplayInfo not saved

	pStream->Read(&m_iNumSessions);
	if (!isNetworkMultiPlayer())
	{
		++m_iNumSessions;
	}

	{
		int iSize;
		m_aPlotExtraYields.clear();
		pStream->Read(&iSize);
		for (int i = 0; i < iSize; ++i)
		{
			PlotExtraYield kPlotYield;
			kPlotYield.read(pStream);
			m_aPlotExtraYields.push_back(kPlotYield);
		}
	}

	{
		int iSize;
		m_aPlotExtraCosts.clear();
		pStream->Read(&iSize);
		for (int i = 0; i < iSize; ++i)
		{
			PlotExtraCost kPlotCost;
			kPlotCost.read(pStream);
			m_aPlotExtraCosts.push_back(kPlotCost);
		}
	}

	{
		int iSize;
		m_mapVoteSourceReligions.clear();
		pStream->Read(&iSize);
		for (int i = 0; i < iSize; ++i)
		{
			VoteSourceTypes eVoteSource;
			ReligionTypes eReligion;
			pStream->Read((int*)&eVoteSource);
			pStream->Read((int*)&eReligion);
			m_mapVoteSourceReligions[eVoteSource] = eReligion;
		}
	}

	{
		int iSize;
		m_aeInactiveTriggers.clear();
		pStream->Read(&iSize);
		for (int i = 0; i < iSize; ++i)
		{
			int iTrigger;
			pStream->Read(&iTrigger);
			m_aeInactiveTriggers.push_back((EventTriggerTypes)iTrigger);
		}
	}

	// Get the active player information from the initialization structure
	if (!isGameMultiPlayer())
	{
		for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isHuman())
			{
				setActivePlayer((PlayerTypes)iI);
				break;
			}
		}
		addReplayMessage(REPLAY_MESSAGE_MAJOR_EVENT, getActivePlayer(), gDLL->getText("TXT_KEY_MISC_RELOAD", m_iNumSessions));
	}

	if (isOption(GAMEOPTION_NEW_RANDOM_SEED))
	{
		if (!isNetworkMultiPlayer())
		{
			m_sorenRand.reseed(timeGetTime());
		}
	}

	pStream->Read(&m_iShrineBuildingCount);
	pStream->Read(GC.getNumBuildingInfos(), m_aiShrineBuilding);
	pStream->Read(GC.getNumBuildingInfos(), m_aiShrineReligion);
	pStream->Read(&m_iNumCultureVictoryCities);
	pStream->Read(&m_eCultureVictoryCultureLevel);


	//Rhye - start (RFCMP)
	long result = 0;
	CyArgsList argsList;
	argsList.add(-1); //useless
	gDLL->getPythonIFace()->callFunction(PYScreensModule, "resetStabilityParameters", argsList.makeFunctionArgs(), &result);
	//Rhye - end
}


void CvGame::write(FDataStreamBase* pStream)
{
	int iI;

	uint uiFlag=1;
	pStream->Write(uiFlag);		// flag for expansion

	pStream->Write(m_iElapsedGameTurns);
	pStream->Write(m_iStartTurn);
	pStream->Write(m_iStartYear);
	pStream->Write(m_iEstimateEndTurn);
	pStream->Write(m_iTurnSlice);
	pStream->Write(m_iCutoffSlice);
	pStream->Write(m_iNumGameTurnActive);
	pStream->Write(m_iNumCities);
	pStream->Write(m_iTotalPopulation);
	pStream->Write(m_iTradeRoutes);
	pStream->Write(m_iFreeTradeCount);
	pStream->Write(m_iNoNukesCount);
	pStream->Write(m_iNukesExploded);
	pStream->Write(m_iMaxPopulation);
	pStream->Write(m_iMaxLand);
	pStream->Write(m_iMaxTech);
	pStream->Write(m_iMaxWonders);
	pStream->Write(m_iInitPopulation);
	pStream->Write(m_iInitLand);
	pStream->Write(m_iInitTech);
	pStream->Write(m_iInitWonders);
	pStream->Write(m_iAIAutoPlay);
	pStream->Write(m_iCircumnavigated); //Rhye

	// m_uiInitialTime not saved

	pStream->Write(m_bScoreDirty);
	pStream->Write(m_bCircumnavigated);
	// m_bDebugMode not saved
	pStream->Write(m_bFinalInitialized);
	// m_bPbemTurnSent not saved
	pStream->Write(m_bHotPbemBetweenTurns);
	// m_bPlayerOptionsSent not saved
	pStream->Write(m_bNukesValid);

	pStream->Write(m_eHandicap);
	pStream->Write(m_ePausePlayer);
	pStream->Write(m_eBestLandUnit);
	pStream->Write(m_eWinner);
	pStream->Write(m_eVictory);
	pStream->Write(m_eGameState);

	pStream->WriteString(m_szScriptData);

	pStream->Write(MAX_PLAYERS, m_aiRankPlayer);
	pStream->Write(MAX_PLAYERS, m_aiPlayerRank);
	pStream->Write(MAX_PLAYERS, m_aiPlayerScore);
	pStream->Write(MAX_TEAMS, m_aiRankTeam);
	pStream->Write(MAX_TEAMS, m_aiTeamRank);
	pStream->Write(MAX_TEAMS, m_aiTeamScore);

	pStream->Write(GC.getNumUnitInfos(), m_paiUnitCreatedCount);
	pStream->Write(GC.getNumUnitClassInfos(), m_paiUnitClassCreatedCount);
	pStream->Write(GC.getNumBuildingClassInfos(), m_paiBuildingClassCreatedCount);
	pStream->Write(GC.getNumProjectInfos(), m_paiProjectCreatedCount);
	pStream->Write(GC.getNumCivicInfos(), m_paiForceCivicCount);
	pStream->Write(GC.getNumVoteInfos(), (int*)m_paiVoteOutcome);
	pStream->Write(GC.getNumReligionInfos(), m_paiReligionGameTurnFounded);
	pStream->Write(GC.getNumCorporationInfos(), m_paiCorporationGameTurnFounded);
	pStream->Write(GC.getNumVoteSourceInfos(), m_aiSecretaryGeneralTimer);
	pStream->Write(GC.getNumVoteSourceInfos(), m_aiVoteTimer);
	pStream->Write(GC.getNumVoteSourceInfos(), m_aiDiploVote);

	pStream->Write(GC.getNumSpecialUnitInfos(), m_pabSpecialUnitValid);
	pStream->Write(GC.getNumSpecialBuildingInfos(), m_pabSpecialBuildingValid);
	pStream->Write(GC.getNumReligionInfos(), m_abReligionSlotTaken);

	for (iI=0;iI<GC.getNumReligionInfos();iI++)
	{
		pStream->Write(m_paHolyCity[iI].eOwner);
		pStream->Write(m_paHolyCity[iI].iID);
	}

	for (iI=0;iI<GC.getNumCorporationInfos();iI++)
	{
		pStream->Write(m_paHeadquarters[iI].eOwner);
		pStream->Write(m_paHeadquarters[iI].iID);
	}

	{
		std::vector<CvWString>::iterator it;

		pStream->Write(m_aszDestroyedCities.size());
		for (it = m_aszDestroyedCities.begin(); it != m_aszDestroyedCities.end(); it++)
		{
			pStream->WriteString(*it);
		}

		pStream->Write(m_aszGreatPeopleBorn.size());
		for (it = m_aszGreatPeopleBorn.begin(); it != m_aszGreatPeopleBorn.end(); it++)
		{
			pStream->WriteString(*it);
		}
	}

	WriteStreamableFFreeListTrashArray(m_deals, pStream);
	WriteStreamableFFreeListTrashArray(m_voteSelections, pStream);
	WriteStreamableFFreeListTrashArray(m_votesTriggered, pStream);
	pStream->Write(m_iCrusadeRegion);
	pStream->Write(MAX_TEAMS, m_abCrusadeParticipants);
	pStream->Write(MAX_TEAMS, m_abCrusadeTargets);
	pStream->Write(MAX_PLAYERS, m_aiCrusadePlunder);
	pStream->Write(MAX_PLAYERS, m_abCrusadeHolyStates);
	pStream->Write(m_iPapalPlayer);
	pStream->Write(m_iPapalRetryTurn);
	pStream->Write(m_iPapalFirstCouncilTurn);
	pStream->Write(m_iPapalRomeDeadline);
	pStream->Write(m_iPapalDevotionFadeStart);
	pStream->Write(m_iPapalDecisionSerial);
	pStream->Write(m_iPapalRefuser);
	pStream->Write(MAX_CIV_PLAYERS, m_aiPapalRefusalPenalties);
	pStream->Write(m_bPapalPalaceEffects);
	pStream->Write((int)m_papalDecisions.size());
	for (std::map<int, PlayerTypes>::const_iterator p = m_papalDecisions.begin(); p != m_papalDecisions.end(); ++p)
	{ pStream->Write(p->first); pStream->Write((int)p->second); }
	pStream->Write(m_iCrusadeEndTurn);
	pStream->Write(MAX_CIV_PLAYERS, m_aiCrusadeRewards);

	m_mapRand.write(pStream);
	m_sorenRand.write(pStream);

	ReplayMessageList::size_type iSize = m_listReplayMessages.size();
	pStream->Write(iSize);
	ReplayMessageList::const_iterator it;
	for (it = m_listReplayMessages.begin(); it != m_listReplayMessages.end(); it++)
	{
		const CvReplayMessage* pMessage = *it;
		if (NULL != pMessage)
		{
			pMessage->write(*pStream);
		}
	}
	// m_pReplayInfo not saved

	pStream->Write(m_iNumSessions);

	pStream->Write(m_aPlotExtraYields.size());
	for (std::vector<PlotExtraYield>::iterator it = m_aPlotExtraYields.begin(); it != m_aPlotExtraYields.end(); ++it)
	{
		(*it).write(pStream);
	}

	pStream->Write(m_aPlotExtraCosts.size());
	for (std::vector<PlotExtraCost>::iterator it = m_aPlotExtraCosts.begin(); it != m_aPlotExtraCosts.end(); ++it)
	{
		(*it).write(pStream);
	}

	pStream->Write(m_mapVoteSourceReligions.size());
	for (stdext::hash_map<VoteSourceTypes, ReligionTypes>::iterator it = m_mapVoteSourceReligions.begin(); it != m_mapVoteSourceReligions.end(); ++it)
	{
		pStream->Write(it->first);
		pStream->Write(it->second);
	}

	pStream->Write(m_aeInactiveTriggers.size());
	for (std::vector<EventTriggerTypes>::iterator it = m_aeInactiveTriggers.begin(); it != m_aeInactiveTriggers.end(); ++it)
	{
		pStream->Write(*it);
	}

	pStream->Write(m_iShrineBuildingCount);
	pStream->Write(GC.getNumBuildingInfos(), m_aiShrineBuilding);
	pStream->Write(GC.getNumBuildingInfos(), m_aiShrineReligion);
	pStream->Write(m_iNumCultureVictoryCities);
	pStream->Write(m_eCultureVictoryCultureLevel);
}

void CvGame::writeReplay(FDataStreamBase& stream, PlayerTypes ePlayer)
{
	SAFE_DELETE(m_pReplayInfo);
	m_pReplayInfo = new CvReplayInfo();
	if (m_pReplayInfo)
	{
		m_pReplayInfo->createInfo(ePlayer);

		m_pReplayInfo->write(stream);
	}
}

void CvGame::saveReplay(PlayerTypes ePlayer)
{
	gDLL->getEngineIFace()->SaveReplay(ePlayer);
}


void CvGame::showEndGameSequence()
{
	CvPopupInfo* pInfo;
	CvWString szBuffer;
	int iI;

	long iHours = getMinutesPlayed() / 60;
	long iMinutes = getMinutesPlayed() % 60;

	for (iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		CvPlayer& player = GET_PLAYER((PlayerTypes)iI);
		if (player.isHuman())
		{
			addReplayMessage(REPLAY_MESSAGE_MAJOR_EVENT, (PlayerTypes)iI, gDLL->getText("TXT_KEY_MISC_TIME_SPENT", iHours, iMinutes));

			pInfo = new CvPopupInfo(BUTTONPOPUP_TEXT);
			if (NULL != pInfo)
			{
				if ((getWinner() != NO_TEAM) && (getVictory() != NO_VICTORY))
				{
					//Rhye - start
					//pInfo->setText(gDLL->getText("TXT_KEY_GAME_WON", GET_TEAM(getWinner()).getName().GetCString(), GC.getVictoryInfo(getVictory()).getTextKeyWide()));
					pInfo->setText(gDLL->getText("TXT_KEY_GAME_WON", GET_PLAYER((PlayerTypes)getWinner()).getCivilizationShortDescription(), GC.getVictoryInfo(getVictory()).getTextKeyWide()));
					//Rhye - end
				}
				else
				{
					//pInfo->setText(gDLL->getText("TXT_KEY_MISC_DEFEAT")); //Rhye
					pInfo->setText(gDLL->getText("TXT_KEY_MISC_DEFEAT2")); //Rhye
				}
				player.addPopup(pInfo);
			}

			if (getWinner() == player.getTeam())
			{
				if (!CvString(GC.getVictoryInfo(getVictory()).getMovie()).empty())
				{
					// show movie
					pInfo = new CvPopupInfo(BUTTONPOPUP_PYTHON_SCREEN);
					if (NULL != pInfo)
					{
						pInfo->setText(L"showVictoryMovie");
						pInfo->setData1((int)getVictory());
						player.addPopup(pInfo);
					}
				}
				else if (GC.getVictoryInfo(getVictory()).isDiploVote())
				{
					pInfo = new CvPopupInfo(BUTTONPOPUP_PYTHON_SCREEN);
					if (NULL != pInfo)
					{
						pInfo->setText(L"showUnVictoryScreen");
						player.addPopup(pInfo);
					}
				}
			}

			// show replay
			pInfo = new CvPopupInfo(BUTTONPOPUP_PYTHON_SCREEN);
			if (NULL != pInfo)
			{
				pInfo->setText(L"showReplay"); 
				pInfo->setData1(iI);
				pInfo->setOption1(false); // don't go to HOF on exit
				player.addPopup(pInfo);
			}

			// show top cities / stats
			pInfo = new CvPopupInfo(BUTTONPOPUP_PYTHON_SCREEN);
			if (NULL != pInfo)
			{
				pInfo->setText(L"showInfoScreen");
				pInfo->setData1(0);
				pInfo->setData2(1);
				player.addPopup(pInfo);
			}

			// show Dan
			pInfo = new CvPopupInfo(BUTTONPOPUP_PYTHON_SCREEN);
			if (NULL != pInfo)
			{
				pInfo->setText(L"showDanQuayleScreen");
				player.addPopup(pInfo);
			}

			// show Hall of Fame
			pInfo = new CvPopupInfo(BUTTONPOPUP_PYTHON_SCREEN);
			if (NULL != pInfo)
			{
				pInfo->setText(L"showHallOfFame");
				player.addPopup(pInfo);
			}
		}
	}
}

CvReplayInfo* CvGame::getReplayInfo() const
{
	return m_pReplayInfo;
}

void CvGame::setReplayInfo(CvReplayInfo* pReplay)
{
	SAFE_DELETE(m_pReplayInfo);
	m_pReplayInfo = pReplay;
}

bool CvGame::hasSkippedSaveChecksum() const
{
	return gDLL->hasSkippedSaveChecksum();
}

void CvGame::addPlayer(PlayerTypes eNewPlayer, LeaderHeadTypes eLeader, CivilizationTypes eCiv)
{
	PlayerColorTypes eColor = (PlayerColorTypes)GC.getCivilizationInfo(eCiv).getDefaultPlayerColor();

	for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
	{
		if (eColor == NO_PLAYERCOLOR || GET_PLAYER((PlayerTypes)iI).getPlayerColor() == eColor)
		{
			for (int iK = 0; iK < GC.getNumPlayerColorInfos(); iK++)
			{
				if (iK != GC.getCivilizationInfo((CivilizationTypes)GC.getDefineINT("BARBARIAN_CIVILIZATION")).getDefaultPlayerColor())
				{
					bool bValid = true;

					for (int iL = 0; iL < MAX_CIV_PLAYERS; iL++)
					{
						if (GET_PLAYER((PlayerTypes)iL).getPlayerColor() == iK)
						{
							bValid = false;
							break;
						}
					}

					if (bValid)
					{
						eColor = (PlayerColorTypes)iK;
						iI = MAX_CIV_PLAYERS;
						break;
					}
				}
			}
		}
	}

	TeamTypes eTeam = GET_PLAYER(eNewPlayer).getTeam();
	GC.getInitCore().setLeader(eNewPlayer, eLeader);
	GC.getInitCore().setCiv(eNewPlayer, eCiv);
	GC.getInitCore().setSlotStatus(eNewPlayer, SS_COMPUTER);
	GC.getInitCore().setColor(eNewPlayer, eColor);
	GET_TEAM(eTeam).init(eTeam);
	GET_PLAYER(eNewPlayer).init(eNewPlayer);
}

bool CvGame::isCompetingCorporation(CorporationTypes eCorporation1, CorporationTypes eCorporation2) const
{
	bool bShareResources = false;

	for (int i = 0; i < GC.getNUM_CORPORATION_PREREQ_BONUSES() && !bShareResources; ++i)
	{
		if (GC.getCorporationInfo(eCorporation1).getPrereqBonus(i) != NO_BONUS)
		{
			for (int j = 0; j < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++j)
			{
				if (GC.getCorporationInfo(eCorporation2).getPrereqBonus(j) != NO_BONUS)
				{
					if (GC.getCorporationInfo(eCorporation1).getPrereqBonus(i) == GC.getCorporationInfo(eCorporation2).getPrereqBonus(j))
					{
						return true;
					}
				}
			}
		}
	}

	return false;
}

int CvGame::getPlotExtraYield(int iX, int iY, YieldTypes eYield) const
{
	for (std::vector<PlotExtraYield>::const_iterator it = m_aPlotExtraYields.begin(); it != m_aPlotExtraYields.end(); ++it)
	{
		if ((*it).m_iX == iX && (*it).m_iY == iY)
		{
			return (*it).m_aeExtraYield[eYield];
		}
	}

	return 0;
}

void CvGame::setPlotExtraYield(int iX, int iY, YieldTypes eYield, int iExtraYield)
{
	bool bFound = false;

	for (std::vector<PlotExtraYield>::iterator it = m_aPlotExtraYields.begin(); it != m_aPlotExtraYields.end(); ++it)
	{
		if ((*it).m_iX == iX && (*it).m_iY == iY)
		{
			(*it).m_aeExtraYield[eYield] += iExtraYield;
			bFound = true;
			break;
		}
	}

	if (!bFound)
	{
		PlotExtraYield kExtraYield;
		kExtraYield.m_iX = iX;
		kExtraYield.m_iY = iY;
		for (int i = 0; i < NUM_YIELD_TYPES; ++i)
		{
			if (eYield == i)
			{
				kExtraYield.m_aeExtraYield.push_back(iExtraYield);
			}
			else
			{
				kExtraYield.m_aeExtraYield.push_back(0);
			}
		}
		m_aPlotExtraYields.push_back(kExtraYield);
	}

	CvPlot* pPlot = GC.getMapINLINE().plot(iX, iY);
	if (NULL != pPlot)
	{
		pPlot->updateYield();
	}
}

void CvGame::removePlotExtraYield(int iX, int iY)
{
	for (std::vector<PlotExtraYield>::iterator it = m_aPlotExtraYields.begin(); it != m_aPlotExtraYields.end(); ++it)
	{
		if ((*it).m_iX == iX && (*it).m_iY == iY)
		{
			m_aPlotExtraYields.erase(it);
			break;
		}
	}

	CvPlot* pPlot = GC.getMapINLINE().plot(iX, iY);
	if (NULL != pPlot)
	{
		pPlot->updateYield();
	}
}

int CvGame::getPlotExtraCost(int iX, int iY) const
{
	for (std::vector<PlotExtraCost>::const_iterator it = m_aPlotExtraCosts.begin(); it != m_aPlotExtraCosts.end(); ++it)
	{
		if ((*it).m_iX == iX && (*it).m_iY == iY)
		{
			return (*it).m_iCost;
		}
	}

	return 0;
}

void CvGame::changePlotExtraCost(int iX, int iY, int iCost)
{
	bool bFound = false;

	for (std::vector<PlotExtraCost>::iterator it = m_aPlotExtraCosts.begin(); it != m_aPlotExtraCosts.end(); ++it)
	{
		if ((*it).m_iX == iX && (*it).m_iY == iY)
		{
			(*it).m_iCost += iCost;
			bFound = true;
			break;
		}
	}

	if (!bFound)
	{
		PlotExtraCost kExtraCost;
		kExtraCost.m_iX = iX;
		kExtraCost.m_iY = iY;
		kExtraCost.m_iCost = iCost;
		m_aPlotExtraCosts.push_back(kExtraCost);
	}
}

void CvGame::removePlotExtraCost(int iX, int iY)
{
	for (std::vector<PlotExtraCost>::iterator it = m_aPlotExtraCosts.begin(); it != m_aPlotExtraCosts.end(); ++it)
	{
		if ((*it).m_iX == iX && (*it).m_iY == iY)
		{
			m_aPlotExtraCosts.erase(it);
			break;
		}
	}
}

ReligionTypes CvGame::getVoteSourceReligion(VoteSourceTypes eVoteSource) const
{
	stdext::hash_map<VoteSourceTypes, ReligionTypes>::const_iterator it;

	it = m_mapVoteSourceReligions.find(eVoteSource);
	if (it == m_mapVoteSourceReligions.end())
	{
		return NO_RELIGION;
	}

	return it->second;
}

void CvGame::setVoteSourceReligion(VoteSourceTypes eVoteSource, ReligionTypes eReligion, bool bAnnounce)
{
	m_mapVoteSourceReligions[eVoteSource] = eReligion;

	if (bAnnounce)
	{
		if (NO_RELIGION != eReligion)
		{
			CvWString szBuffer = gDLL->getText("TXT_KEY_VOTE_SOURCE_RELIGION", GC.getReligionInfo(eReligion).getTextKeyWide(), GC.getReligionInfo(eReligion).getAdjectiveKey(), GC.getVoteSourceInfo(eVoteSource).getTextKeyWide());

			for (int iI = 0; iI < MAX_PLAYERS; iI++)
			{
				if (GET_PLAYER((PlayerTypes)iI).isAlive())
				{
					gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, GC.getReligionInfo(eReligion).getSound(), MESSAGE_TYPE_MAJOR_EVENT, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"));
				}
			}
		}
	}
}


// CACHE: cache frequently used values
///////////////////////////////////////


int CvGame::getShrineBuildingCount(ReligionTypes eReligion)
{
	int	iShrineBuildingCount = 0;

	if (eReligion == NO_RELIGION)
		iShrineBuildingCount = m_iShrineBuildingCount;
	else for (int iI = 0; iI < m_iShrineBuildingCount; iI++)
		if (m_aiShrineReligion[iI] == eReligion)
			iShrineBuildingCount++;

	return iShrineBuildingCount;
}

BuildingTypes CvGame::getShrineBuilding(int eIndex, ReligionTypes eReligion)
{
	FAssertMsg(eIndex >= 0 && eIndex < m_iShrineBuildingCount, "invalid index to CvGame::getShrineBuilding");

	BuildingTypes eBuilding = NO_BUILDING;

	if (eIndex >= 0 && eIndex < m_iShrineBuildingCount)
	{
		if (eReligion == NO_RELIGION)
			eBuilding = (BuildingTypes) m_aiShrineBuilding[eIndex];
		else for (int iI = 0, iReligiousBuilding = 0; iI < m_iShrineBuildingCount; iI++)
			if (m_aiShrineReligion[iI] == (int) eReligion)
			{
				if (iReligiousBuilding == eIndex)
				{
					// found it
					eBuilding = (BuildingTypes) m_aiShrineBuilding[iI];
					break;
				}

				iReligiousBuilding++;
			}
	}

	return eBuilding;
}

void CvGame::changeShrineBuilding(BuildingTypes eBuilding, ReligionTypes eReligion, bool bRemove)
{
	FAssertMsg(eBuilding >= 0 && eBuilding < GC.getNumBuildingInfos(), "invalid index to CvGame::changeShrineBuilding");
	FAssertMsg(bRemove || m_iShrineBuildingCount < GC.getNumBuildingInfos(), "trying to add too many buildings to CvGame::changeShrineBuilding");

	if (bRemove)
	{
		bool bFound = false;

		for (int iI = 0; iI < m_iShrineBuildingCount; iI++)
		{
			if (!bFound)
			{
				// note, eReligion is not important if we removing, since each building is always one religion
				if (m_aiShrineBuilding[iI] == (int) eBuilding)
					bFound = true;
			}
			
			if (bFound)
			{
				int iToMove = iI + 1;
				if (iToMove < m_iShrineBuildingCount)
				{
					m_aiShrineBuilding[iI] = m_aiShrineBuilding[iToMove];
					m_aiShrineReligion[iI] = m_aiShrineReligion[iToMove];
				}
				else
				{
					m_aiShrineBuilding[iI] = (int) NO_BUILDING;
					m_aiShrineReligion[iI] = (int) NO_RELIGION;
				}
			}

		if (bFound)
			m_iShrineBuildingCount--;

		}
	}
	else if (m_iShrineBuildingCount < GC.getNumBuildingInfos())
	{
		// add this item to the end
		m_aiShrineBuilding[m_iShrineBuildingCount] = eBuilding;
		m_aiShrineReligion[m_iShrineBuildingCount] = eReligion;
		m_iShrineBuildingCount++;
	}
	
}

bool CvGame::culturalVictoryValid()
{
	if (m_iNumCultureVictoryCities > 0)
	{
		return true;
	}

	return false;
}

int CvGame::culturalVictoryNumCultureCities()
{
	return m_iNumCultureVictoryCities;
}

CultureLevelTypes CvGame::culturalVictoryCultureLevel()
{
	if (m_iNumCultureVictoryCities > 0)
	{
		return (CultureLevelTypes) m_eCultureVictoryCultureLevel;
	}
	
	return NO_CULTURELEVEL;
}

int CvGame::getCultureThreshold(CultureLevelTypes eLevel) const
{
	int iThreshold = GC.getCultureLevelInfo(eLevel).getSpeedThreshold(getGameSpeedType());
	if (isOption(GAMEOPTION_NO_ESPIONAGE))
	{
		iThreshold *= 100 + GC.getDefineINT("NO_ESPIONAGE_CULTURE_LEVEL_MODIFIER");
		iThreshold /= 100;
	}
	return iThreshold;
}

void CvGame::doUpdateCacheOnTurn()
{
	OBSERVER_PERFORMANCE("CvGame::doUpdateCacheOnTurn");
	int	iI;
	
	// reset shrine count
	m_iShrineBuildingCount = 0;

	for (iI = 0; iI < GC.getNumBuildingInfos(); iI++)
	{
		CvBuildingInfo&	kBuildingInfo = GC.getBuildingInfo((BuildingTypes) iI);
		
		// if it is for holy city, then its a shrine-thing, add it
		if (kBuildingInfo.getHolyCity() != NO_RELIGION)
		{
			changeShrineBuilding((BuildingTypes) iI, (ReligionTypes) kBuildingInfo.getReligionType());
		}
	}

	// reset cultural victories
	m_iNumCultureVictoryCities = 0;
	for (iI = 0; iI < GC.getNumVictoryInfos(); iI++)
	{
		if (isVictoryValid((VictoryTypes) iI))
		{
			CvVictoryInfo& kVictoryInfo = GC.getVictoryInfo((VictoryTypes) iI);
			if (kVictoryInfo.getCityCulture() > 0)
			{
				int iNumCultureCities = kVictoryInfo.getNumCultureCities();
				if (iNumCultureCities > m_iNumCultureVictoryCities)
				{
					m_iNumCultureVictoryCities = iNumCultureCities;
					m_eCultureVictoryCultureLevel = kVictoryInfo.getCityCulture();
				}
			}
		}
	}
}

VoteSelectionData* CvGame::getVoteSelection(int iID) const
{
	return ((VoteSelectionData*)(m_voteSelections.getAt(iID)));
}

bool CvGame::isApostolicCouncil(VoteSourceTypes eSource) const
{
	return eSource == GC.getInfoTypeForString("DIPLOVOTE_POPE");
}

CvCity* CvGame::getApostolicPalace() const
{
	BuildingTypes ePalace = (BuildingTypes)GC.getInfoTypeForString("BUILDING_APOSTOLIC_PALACE");
	for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)i);
		if (!kPlayer.isAlive() || kPlayer.getBuildingClassCount((BuildingClassTypes)GC.getBuildingInfo(ePalace).getBuildingClassType()) == 0) continue;
		int iLoop;
		for (CvCity* pCity = kPlayer.firstCity(&iLoop); pCity; pCity = kPlayer.nextCity(&iLoop))
			if (pCity->getNumRealBuilding(ePalace) > 0) return pCity;
	}
	return NULL;
}

bool CvGame::isCouncilActive() const
{
	// This tracks applied effects. Refresh around civic/religion changes so
	// removal runs while the old source is still active, without stranded yields.
	return m_bPapalPalaceEffects;
}

CvCity* CvGame::getPapalRome() const
{
	CvPlot* pPlot = GC.getMapINLINE().plot(60, 44);
	return pPlot ? pPlot->getPlotCity() : NULL;
}

bool CvGame::isPapalState(PlayerTypes ePlayer) const { return ePlayer != NO_PLAYER && ePlayer == m_iPapalPlayer; }

bool CvGame::canFoundPapacy(PlayerTypes ePlayer) const
{
	CvCity* pRome = getPapalRome();
	if (m_iPapalPlayer != NO_PLAYER || GET_PLAYER((PlayerTypes)PAPAL_STATE).isAlive() || !pRome || pRome->getOwnerINLINE() != ePlayer || !pRome->isHasReligion((ReligionTypes)GC.getInfoTypeForString("RELIGION_CHRISTIANITY"))) return false;
	CvPlayer& kOwner = GET_PLAYER(ePlayer);
	if (kOwner.isBarbarian() || kOwner.isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_TOLERANCE")) || kOwner.isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_STATE_ATHEISM"))) return false;
	bool bIndependent = kOwner.getCivilizationType() == GC.getInfoTypeForString("CIVILIZATION_INDEPENDENT") || kOwner.getCivilizationType() == GC.getInfoTypeForString("CIVILIZATION_INDEPENDENT2");
	return bIndependent || kOwner.getStateReligion() == GC.getInfoTypeForString("RELIGION_CHRISTIANITY");
}

bool CvGame::canBecomePapacy(PlayerTypes ePlayer) const
{
	// Rome may form a minor Papal State; a major empire cannot become one.
	return false;
}

bool CvGame::isPapalDecisionValid(PlayerTypes ePlayer, int iDecision) const
{
	std::map<int, PlayerTypes>::const_iterator it = m_papalDecisions.find(iDecision);
	return it != m_papalDecisions.end() && it->second == ePlayer && canFoundPapacy(ePlayer);
}

void CvGame::disablePapalPalaceEffects()
{
	if (!m_bPapalPalaceEffects) return;
	CvCity* pPalace = getApostolicPalace();
	if (pPalace && !GET_PLAYER(pPalace->getOwnerINLINE()).isBuildingObsolete((BuildingTypes)GC.getInfoTypeForString("BUILDING_APOSTOLIC_PALACE")))
		pPalace->processBuilding((BuildingTypes)GC.getInfoTypeForString("BUILDING_APOSTOLIC_PALACE"), -1, false, true);
	m_bPapalPalaceEffects = false;
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("papal_palace_effects", m_iPapalPlayer, 0);
#endif
	if (pPalace)
	{
		pPalace->updateBuildingCommerce();
		pPalace->updateCommerce(COMMERCE_GOLD);
		pPalace->updateExtraSpecialistYield();
		pPalace->updateExtraBuildingHappiness();
		pPalace->updateExtraBuildingHealth();
	}
}

#if ARFC_ENABLE_REPORTING
void CvGame::reportApostolicMechanic(const char* event, int player, int a, int b, int c, int d, int e, int f, int g, int h) const
{
	if (!isObserverAutoPlay() || isGameMultiPlayer() || g_observerPerformance) return;
	int values[] = {a, b, c, d, e, f, g, h};
	CyArgsList args;
	args.add(event); args.add(player); args.add(values, 8);
	if (!gDLL->getPythonIFace()->callFunction("CvEventInterface", "recordApostolicMechanic", args.makeFunctionArgs()))
		gDLL->logMsg("PythonErr.log", "Awakened RFC: apostolic mechanic recording callback failed.", false, false);
}


#endif

void CvGame::clearPapalRefusalPenalties()
{
	if (m_iPapalRefuser == NO_PLAYER) return;

	for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
	{
		if (m_aiPapalRefusalPenalties[i] != 0)
		{
#if ARFC_ENABLE_REPORTING
			int iPreviousAttitude = GET_PLAYER((PlayerTypes)i).AI_getAttitudeExtra((PlayerTypes)m_iPapalRefuser);
#endif
			GET_PLAYER((PlayerTypes)i).AI_changeAttitudeExtra((PlayerTypes)m_iPapalRefuser, m_aiPapalRefusalPenalties[i]);
#if ARFC_ENABLE_REPORTING
			reportApostolicMechanic("papal_penalty_cleared", m_iPapalRefuser, i, m_aiPapalRefusalPenalties[i], iPreviousAttitude, GET_PLAYER((PlayerTypes)i).AI_getAttitudeExtra((PlayerTypes)m_iPapalRefuser));
#endif
		}
		m_aiPapalRefusalPenalties[i] = 0;
	}
	m_iPapalRefuser = NO_PLAYER;
}

void CvGame::refreshPapalPalaceEffects()
{
	CvCity* pRome = getPapalRome();
	if (pRome != NULL && isPapalState(pRome->getOwnerINLINE()))
	{
		m_iPapalRomeDeadline = -1;
		// Claim the first ring immediately on founding or recapture, even when
		// the Palace is inactive. Culture updates keep these borders protected.
		for (int i = 0; i < NUM_DIRECTION_TYPES; ++i)
		{
			CvPlot* pPlot = plotDirection(pRome->getX_INLINE(), pRome->getY_INLINE(), (DirectionTypes)i);
			if (pPlot != NULL) pPlot->updateCulture(true, true);
		}
	}
	if (m_iPapalRefuser != NO_PLAYER && (!pRome || pRome->getOwnerINLINE() != m_iPapalRefuser)) clearPapalRefusalPenalties();
	BuildingTypes ePalace = (BuildingTypes)GC.getInfoTypeForString("BUILDING_APOSTOLIC_PALACE");
	bool bEnable = pRome && isPapalState(pRome->getOwnerINLINE()) && pRome->getNumRealBuilding(ePalace) > 0 &&
		GET_PLAYER(pRome->getOwnerINLINE()).getStateReligion() == GC.getInfoTypeForString("RELIGION_CHRISTIANITY") &&
		!GET_PLAYER(pRome->getOwnerINLINE()).isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_TOLERANCE")) &&
		!GET_PLAYER(pRome->getOwnerINLINE()).isBuildingObsolete(ePalace);
	if (bEnable == m_bPapalPalaceEffects) return;
	if (!bEnable) disablePapalPalaceEffects();
	else
	{
		m_bPapalPalaceEffects = true;
		pRome->processBuilding(ePalace, 1, false, true);
		pRome->updateCommerce(COMMERCE_GOLD);
#if ARFC_ENABLE_REPORTING
		reportApostolicMechanic("papal_palace_effects", m_iPapalPlayer, 1);
#endif
	}
	gDLL->getInterfaceIFace()->setDirty(CityScreen_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(GameData_DIRTY_BIT, true);
}

void CvGame::announcePapalCouncil(const char* szEvent)
{
    const ReligionTypes eChristianity = (ReligionTypes)GC.getInfoTypeForString("RELIGION_CHRISTIANITY");
    for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
    {
        CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)i);
        // Retain Christian affiliation under Tolerance, which hides state religion.
        if (!kPlayer.isAlive() || kPlayer.getLastStateReligion() != eChristianity) continue;
        const char* szTone = "CASUAL";
        if (kPlayer.isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_TOLERANCE")) ||
            kPlayer.isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_STATE_ATHEISM"))) szTone = "SCEPTICAL";
        else if (kPlayer.isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_GOD_STATE"))) szTone = "DEVOUT";
        else if (kPlayer.isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_STATE_RELIGION"))) szTone = "RESPECTFUL";
        const CvString szKey = CvString::format("TXT_KEY_AP_COUNCIL_%s_%s", szEvent, szTone);
        const CvWString szText = gDLL->getText(szKey.c_str(), std::max(0, m_iPapalFirstCouncilTurn - getGameTurn()));
        gDLL->getInterfaceIFace()->addMessage((PlayerTypes)i, false, GC.getEVENT_MESSAGE_TIME(),
            szText, NULL, MESSAGE_TYPE_MAJOR_EVENT, NULL,
            (ColorTypes)GC.getInfoTypeForString("COLOR_WHITE"), 60, 44);
        if (kPlayer.isHuman())
        {
            // Informational only: addressed delivery, with no gameplay callback.
            CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_TEXT);
            if (pInfo) { pInfo->setText(szText); gDLL->getInterfaceIFace()->addPopup(pInfo, (PlayerTypes)i); }
        }
    }
}

void CvGame::notifyPapalRomeLost(PlayerTypes eOwner)
{
	if (!isPapalState(eOwner) || !GET_PLAYER(eOwner).isAlive() || m_iPapalRomeDeadline >= 0) return;
	m_iPapalRomeDeadline = getGameTurn() + 10;
	gDLL->getInterfaceIFace()->addMessage(eOwner, false, GC.getEVENT_MESSAGE_TIME(),
		gDLL->getText("TXT_KEY_AP_ROME_RECOVERY", 10), NULL, MESSAGE_TYPE_MAJOR_EVENT, NULL,
		(ColorTypes)GC.getInfoTypeForString("COLOR_WARNING_TEXT"), 60, 44);
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("papal_rome_lost", eOwner, m_iPapalRomeDeadline);
#endif
}

bool CvGame::canPapalSurviveWithoutCities(PlayerTypes ePlayer) const
{
	return isPapalState(ePlayer) && m_iPapalRomeDeadline >= 0 && GC.getInitCore().getGameTurn() <= m_iPapalRomeDeadline;
}

int CvGame::getPapalDevotionPercent(PlayerTypes ePlayer) const
{
	if (!isPapalState(ePlayer) || !GET_PLAYER(ePlayer).isAlive()) return 0;
	if (m_iPapalDevotionFadeStart < 0) return 100;
	const int iDuration = std::max(1, 30 * GC.getGameSpeedInfo(getGameSpeedType()).getVictoryDelayPercent() / 100);
	return std::max(0, 100 * (iDuration - std::max(0, GC.getInitCore().getGameTurn() - m_iPapalDevotionFadeStart)) / iDuration);
}

void CvGame::doPapalLifecycle()
{
	if (m_iPapalPlayer == NO_PLAYER) return;
	const PlayerTypes ePope = (PlayerTypes)m_iPapalPlayer;
	CvPlayer& kPope = GET_PLAYER(ePope);
	if (kPope.isAlive())
	{
		if (m_iPapalDevotionFadeStart < 0 && getCurrentEra() >= GC.getInfoTypeForString("ERA_MODERN"))
			m_iPapalDevotionFadeStart = getGameTurn();
		CvCity* pRome = getPapalRome();
		if (pRome != NULL && pRome->getOwnerINLINE() == ePope)
		{
			m_iPapalRomeDeadline = -1;
			return;
		}
		notifyPapalRomeLost(ePope);
		if (getGameTurn() < m_iPapalRomeDeadline) return;
		disablePapalPalaceEffects();
		// Release cities peacefully rather than razing them or giving the
		// conqueror a second empire. No conquest rewards or fresh recruitment.
		while (kPope.getNumCities() > 0)
		{
			int iLoop;
			CvCity* pCity = kPope.firstCity(&iLoop);
			CvPlot* pPlot = pCity->plot();
			const int iCulture = pCity->getCultureTimes100(ePope);
			const PlayerTypes eRecipient = GET_PLAYER((PlayerTypes)INDEPENDENT).getNumCities() <=
				GET_PLAYER((PlayerTypes)INDEPENDENT2).getNumCities() ? (PlayerTypes)INDEPENDENT : (PlayerTypes)INDEPENDENT2;
			GET_PLAYER(eRecipient).acquireCity(pCity, false, true, false);
			pCity = pPlot->getPlotCity();
			pCity->setCultureTimes100(eRecipient, pCity->getCultureTimes100(eRecipient) + iCulture, false, false);
			pCity->setCultureTimes100(ePope, 0, false, false);
			const int iPlotCulture = pPlot->getCulture(ePope);
			pPlot->changeCulture(eRecipient, iPlotCulture, false);
			pPlot->setCulture(ePope, 0, true, false);
		}
		kPope.setAlive(false); // Disband remaining units as in ordinary elimination.
#if ARFC_ENABLE_REPORTING
		reportApostolicMechanic("papal_dissolved", ePope, m_iPapalRomeDeadline);
#endif
	}
	announcePapalCouncil("DISSOLVED");
	m_iPapalFirstCouncilTurn = -1;
	// Death clears the identity, so a later eligible Rome event can restore it.
	disablePapalPalaceEffects();
	clearPapalRefusalPenalties();
	m_iPapalPlayer = NO_PLAYER;
	m_iPapalRomeDeadline = -1;
	m_iPapalDevotionFadeStart = -1;
	m_iPapalRetryTurn = getGameTurn();
	gDLL->getInterfaceIFace()->setDirty(Flag_DIRTY_BIT, true);
	m_papalDecisions.clear();
}

void CvGame::doPapalFounding()
{
	doPapalLifecycle();
	refreshPapalPalaceEffects();
	for (std::map<int, PlayerTypes>::iterator it = m_papalDecisions.begin(); it != m_papalDecisions.end(); )
		if (!canFoundPapacy(it->second)) m_papalDecisions.erase(it++); else ++it;
	if (m_iPapalPlayer != NO_PLAYER || !m_papalDecisions.empty()) return;
	CvCity* pRome = getPapalRome();
	if (!pRome || !canFoundPapacy(pRome->getOwnerINLINE())) return;
	PlayerTypes eOwner = pRome->getOwnerINLINE();
	CvPlayer& kOwner = GET_PLAYER(eOwner);
	if (kOwner.getCivilizationType() == GC.getInfoTypeForString("CIVILIZATION_INDEPENDENT") || kOwner.getCivilizationType() == GC.getInfoTypeForString("CIVILIZATION_INDEPENDENT2"))
	{ establishPapacy(eOwner, false); return; }
	if (getGameTurn() < m_iPapalRetryTurn) return;
	int iDecision = m_iPapalDecisionSerial++;
	m_papalDecisions[iDecision] = eOwner;
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("papal_request", eOwner, iDecision, canBecomePapacy(eOwner), kOwner.getNumCities());
#endif
	if (!kOwner.isHuman())
	{ resolvePapalDecision(eOwner, iDecision, canBecomePapacy(eOwner) ? 2 : (kOwner.getNumCities() > 1 ? 0 : 1)); return; }
	CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_PAPAL_FOUNDING);
	if (pInfo) { pInfo->setData1(iDecision); pInfo->setData2(eOwner); gDLL->getInterfaceIFace()->addPopup(pInfo, eOwner); }
}

void CvGame::resolvePapalDecision(PlayerTypes ePlayer, int iDecision, int iChoice)
{
	if (!isPapalDecisionValid(ePlayer, iDecision) || iChoice < 0 || iChoice > 2 || (iChoice == 2 && !canBecomePapacy(ePlayer))) return;
	m_papalDecisions.erase(iDecision); // Consume before transfers and Python events.
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("papal_decision", ePlayer, iDecision, iChoice);
#endif
	if (iChoice == 0 || iChoice == 2) establishPapacy(ePlayer, iChoice == 2);
	else
	{
		if (m_iPapalRefuser != ePlayer) clearPapalRefusalPenalties();
		m_iPapalRefuser = ePlayer;
		for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
			if (i != ePlayer && GET_PLAYER((PlayerTypes)i).isAlive() && GET_PLAYER((PlayerTypes)i).getStateReligion() == GC.getInfoTypeForString("RELIGION_CHRISTIANITY"))
			{
				GET_PLAYER((PlayerTypes)i).AI_changeAttitudeExtra(ePlayer, -2);
				m_aiPapalRefusalPenalties[i] += 2;
#if ARFC_ENABLE_REPORTING
				reportApostolicMechanic("papal_penalty_applied", ePlayer, i, 2, m_aiPapalRefusalPenalties[i], GET_PLAYER((PlayerTypes)i).AI_getAttitudeExtra(ePlayer));
#endif
			}
		announcePapalCouncil("REFUSED");
		m_iPapalRetryTurn = getGameTurn() + std::max(1, GC.getDefineINT("AP_PAPAL_RETRY_TURNS") * GC.getGameSpeedInfo(getGameSpeedType()).getVictoryDelayPercent() / 100);
	}
}

void CvGame::establishPapacy(PlayerTypes eOwner, bool bBecome)
{
	if (!canFoundPapacy(eOwner) || (bBecome && !canBecomePapacy(eOwner))) return;
	clearPapalRefusalPenalties();
	CvCity* pRome = getPapalRome();
	PlayerTypes ePope = bBecome ? eOwner : (PlayerTypes)PAPAL_STATE;
	if (!bBecome)
	{
		GC.getInitCore().setMinorNationCiv(ePope, true);
		addPlayer(ePope, (LeaderHeadTypes)GC.getInfoTypeForString("LEADER_INDEPENDENT"), (CivilizationTypes)GC.getInfoTypeForString("CIVILIZATION_INDEPENDENT"));
	}
	m_iPapalPlayer = ePope;
	GC.getInitCore().setLeaderName(ePope, L"TXT_KEY_AP_POPE");
	// Papal identity applies to the new state and to an owner becoming Pope.
	GC.getInitCore().setColor(ePope, (PlayerColorTypes)GC.getInfoTypeForString("PLAYERCOLOR_PAPAL"));
	gDLL->getEngineIFace()->SetDirty(CultureBorders_DIRTY_BIT, true);
	gDLL->getEngineIFace()->SetDirty(MinimapTexture_DIRTY_BIT, true);
	gDLL->getEngineIFace()->SetDirty(GlobeTexture_DIRTY_BIT, true);
	gDLL->getEngineIFace()->SetDirty(GlobePartialTexture_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(Score_DIRTY_BIT, true);
	gDLL->getInterfaceIFace()->setDirty(Flag_DIRTY_BIT, true);
	m_iPapalRomeDeadline = -1;
	// Each incarnation is devout again, even when founded in the modern world.
	m_iPapalDevotionFadeStart = getCurrentEra() >= GC.getInfoTypeForString("ERA_MODERN") ? getGameTurn() : -1;
	m_bPapalCivicOverride = true;
	CvPlayer& kPope = GET_PLAYER(ePope);
	if (!bBecome)
	{
		kPope.setAlive(true);
		for (int t = 0; t < GC.getNumTechInfos(); ++t)
			if (GET_TEAM(GET_PLAYER(eOwner).getTeam()).isHasTech((TechTypes)t)) GET_TEAM(kPope.getTeam()).setHasTech((TechTypes)t, true, ePope, false, false);
	}
	const char* civics[] = { "CIVIC_MONARCHY", "CIVIC_THEOCRATIC_LEGITIMACY", "CIVIC_GOD_STATE" };
	for (int c = bBecome ? 1 : 0; c < 3; ++c)
	{
		CivicTypes eCivic = (CivicTypes)GC.getInfoTypeForString(civics[c]);
		kPope.setCivics((CivicOptionTypes)GC.getCivicInfo(eCivic).getCivicOptionType(), eCivic);
	}
	kPope.setLastStateReligion((ReligionTypes)GC.getInfoTypeForString("RELIGION_CHRISTIANITY"));
	if (!bBecome) kPope.acquireCity(pRome, false, true, true);
	pRome = getPapalRome();
	kPope.processCivNames();
	pRome->setOccupationTimer(0);
	if (!bBecome)
	{
		pRome->setCultureTimes100(ePope, std::max(10000, pRome->getCultureTimes100(ePope)), false, true);
		pRome->setNumRealBuilding((BuildingTypes)GC.getInfoTypeForString("BUILDING_PALACE"), 1);
		kPope.setCapitalCity(pRome);
		UnitTypes eGuard = pRome->AI_bestUnitAI(UNITAI_CITY_DEFENSE);
		if (eGuard == NO_UNIT) eGuard = (UnitTypes)GC.getInfoTypeForString("UNIT_ARCHER");
		for (int i = 0; i < 2; ++i) { CvUnit* pGuard = kPope.initUnit(eGuard, 60, 44, UNITAI_CITY_DEFENSE); if (pGuard) pGuard->finishMoves(); }
		if (isCrusadeParticipant(eOwner)) joinCrusadeCoalition(ePope);
	}
	setVoteSourceReligion((VoteSourceTypes)GC.getInfoTypeForString("DIPLOVOTE_POPE"), (ReligionTypes)GC.getInfoTypeForString("RELIGION_CHRISTIANITY"));
	pRome->setNumRealBuilding((BuildingTypes)GC.getInfoTypeForString("BUILDING_APOSTOLIC_PALACE"), 1);
	m_bPapalCivicOverride = false;
	refreshPapalPalaceEffects();
	m_iPapalFirstCouncilTurn = std::max(getGameTurn() + 3, getStartTurn() + 10);
	setVoteTimer((VoteSourceTypes)GC.getInfoTypeForString("DIPLOVOTE_POPE"), 0);
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("papacy_founded", ePope, eOwner, bBecome, pRome->getOwnerINLINE(), isCouncilActive());
#endif
	m_papalDecisions.clear();
	announcePapalCouncil("ESTABLISHED");
}

namespace
{
// Geographic fronts on RFC's 124 x 68 world map; earlier regions take precedence.
// Name, west, south, east, north. Coordinates include both endpoints.
struct CrusadeRegion { const char* name; int west, south, east, north; };
const CrusadeRegion crusadeRegions[] = {
	{ "TXT_KEY_AP_REGION_IBERIA", 43, 40, 53, 49 },
	{ "TXT_KEY_AP_REGION_WEST_EUROPE", 43, 50, 61, 58 },
	{ "TXT_KEY_AP_REGION_NORTH_EUROPE", 43, 59, 81, 67 },
	{ "TXT_KEY_AP_REGION_EAST_EUROPE", 62, 50, 81, 58 },
	{ "TXT_KEY_AP_REGION_ITALY_BALKANS", 54, 40, 70, 49 },
	{ "TXT_KEY_AP_REGION_ANATOLIA", 71, 44, 81, 49 },
	{ "TXT_KEY_AP_REGION_LEVANT", 71, 36, 77, 43 },
	{ "TXT_KEY_AP_REGION_EGYPT", 62, 28, 70, 39 },
	{ "TXT_KEY_AP_REGION_MAGHREB", 43, 28, 61, 39 },
	{ "TXT_KEY_AP_REGION_ARABIA", 71, 24, 81, 35 },
	{ "TXT_KEY_AP_REGION_PERSIA", 78, 36, 93, 43 },
	{ "TXT_KEY_AP_REGION_CENTRAL_ASIA", 82, 44, 93, 67 },
	{ "TXT_KEY_AP_REGION_INDIA", 82, 20, 97, 35 },
	{ "TXT_KEY_AP_REGION_EAST_ASIA", 94, 36, 123, 67 },
	{ "TXT_KEY_AP_REGION_SOUTHEAST_ASIA", 98, 20, 123, 35 },
	{ "TXT_KEY_AP_REGION_AFRICA", 43, 0, 81, 27 },
	{ "TXT_KEY_AP_REGION_NORTH_AMERICA", 0, 36, 42, 67 },
	{ "TXT_KEY_AP_REGION_SOUTH_AMERICA", 0, 0, 42, 35 },
	{ "TXT_KEY_AP_REGION_OCEANIA", 82, 0, 123, 19 }
};

bool isChristianTeam(TeamTypes eTeam)
{
	for (int i = 0; i < MAX_PLAYERS; ++i)
		if (GET_PLAYER((PlayerTypes)i).isAlive() && GET_PLAYER((PlayerTypes)i).getTeam() == eTeam &&
			GET_PLAYER((PlayerTypes)i).getStateReligion() == GC.getInfoTypeForString("RELIGION_CHRISTIANITY")) return true;
	return false;
}

int crusadeDuration(const char* key)
{
	return std::max(1, GC.getDefineINT(key) * GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getVictoryDelayPercent() / 100);
}
}

int CvGame::getCrusadeRegionCount() const { return sizeof(crusadeRegions) / sizeof(crusadeRegions[0]); }

int CvGame::getCrusadeRegionAt(const CvPlot* pPlot) const
{
	if (!pPlot) return -1;
	for (int i = 0; i < getCrusadeRegionCount(); ++i)
	{
		const CrusadeRegion& r = crusadeRegions[i];
		if (pPlot->getX_INLINE() >= r.west && pPlot->getX_INLINE() <= r.east && pPlot->getY_INLINE() >= r.south && pPlot->getY_INLINE() <= r.north) return i;
	}
	return -1;
}

CvWString CvGame::getCrusadeRegionName(int iRegion) const
{
	return iRegion >= 0 && iRegion < getCrusadeRegionCount() ? gDLL->getText(crusadeRegions[iRegion].name) : CvWString();
}

bool CvGame::getCrusadeTargets(int iRegion, bool* abTargets) const
{
	for (int t = 0; t < MAX_TEAMS; ++t) abTargets[t] = false;
	if (iRegion < 0 || iRegion >= getCrusadeRegionCount()) return false;
	bool bFrontier = false;
	for (int i = 0; i < MAX_PLAYERS; ++i)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)i);
		if (!kPlayer.isAlive() || kPlayer.isBarbarian() || isChristianTeam(kPlayer.getTeam())) continue;
		int iLoop;
		for (CvCity* pCity = kPlayer.firstCity(&iLoop); pCity; pCity = kPlayer.nextCity(&iLoop))
			if (getCrusadeRegionAt(pCity->plot()) == iRegion) { abTargets[kPlayer.getTeam()] = true; break; }
	}
	// The frontier must be a real land border in this region, not merely nearby capitals.
	const CrusadeRegion& r = crusadeRegions[iRegion];
	for (int x = r.west; x <= r.east && !bFrontier; ++x)
		for (int y = r.south; y <= r.north && !bFrontier; ++y)
		{
			CvPlot* pPlot = GC.getMapINLINE().plot(x, y);
			if (!pPlot || getCrusadeRegionAt(pPlot) != iRegion || pPlot->isWater() || !pPlot->isOwned() || !abTargets[pPlot->getTeam()]) continue;
			for (int d = 0; d < NUM_CARDINALDIRECTION_TYPES; ++d)
			{
				CvPlot* pNext = plotCardinalDirection(x, y, (CardinalDirectionTypes)d);
				if (pNext && !pNext->isWater() && pNext->isOwned() && isChristianTeam(pNext->getTeam())) bFrontier = true;
			}
		}
	// Team-wide war necessarily includes target masters, vassals and defensive allies.
	for (int pass = 0; pass < MAX_TEAMS; ++pass)
	{
		bool bChanged = false;
		for (int t = 0; t < MAX_TEAMS; ++t)
			if (abTargets[t])
				for (int v = 0; v < MAX_TEAMS; ++v)
					if (GET_TEAM((TeamTypes)v).isAlive() && (GET_TEAM((TeamTypes)t).isVassal((TeamTypes)v) || GET_TEAM((TeamTypes)v).isVassal((TeamTypes)t) || GET_TEAM((TeamTypes)t).isDefensivePact((TeamTypes)v)))
					{
						if (isChristianTeam((TeamTypes)v)) return false;
						if (!abTargets[v]) { abTargets[v] = true; bChanged = true; }
					}
		if (!bChanged) break;
	}
	return bFrontier;
}

bool CvGame::canStartCrusade(int iRegion) const
{
	if (!GC.getGameINLINE().isReligionFounded((ReligionTypes)GC.getInfoTypeForString("RELIGION_ISLAM"))) return false;
	if (m_iCrusadeRegion >= 0 || isOption(GAMEOPTION_ALWAYS_PEACE) || isOption(GAMEOPTION_ALWAYS_WAR) || isOption(GAMEOPTION_NO_CHANGING_WAR_PEACE)) return false;
	bool abTargets[MAX_TEAMS];
	if (!getCrusadeTargets(iRegion, abTargets)) return false;
	VoteSourceTypes eSource = (VoteSourceTypes)GC.getInfoTypeForString("DIPLOVOTE_POPE");
	for (int p = 0; p < MAX_TEAMS; ++p)
	{
		CvTeam& kTeam = GET_TEAM((TeamTypes)p);
		if (!kTeam.isAlive() || !kTeam.isVotingMember(eSource)) continue;
		TeamTypes eCommander = (TeamTypes)p;
		for (int m = 0; m < MAX_TEAMS; ++m) if (kTeam.isVassal((TeamTypes)m)) eCommander = (TeamTypes)m;
		if (!GET_TEAM(eCommander).isVotingMember(eSource)) return false;
		for (int t = 0; t < MAX_TEAMS; ++t)
		{
			if (!abTargets[t]) continue;
			CvTeam& kEnemy = GET_TEAM((TeamTypes)t);
			if (kTeam.isArabianJihadWar((TeamTypes)t) || kTeam.isPermanentWarPeace((TeamTypes)t) || kEnemy.isPermanentWarPeace((TeamTypes)p) || kTeam.isDefensivePact((TeamTypes)t)) return false;
			// Avoid a target's defensive alliance turning council members against one another.
			if (kEnemy.isDefensivePact(eCommander)) return false;
			if (!GET_TEAM(eCommander).isAtWar((TeamTypes)t) &&
				(!GET_TEAM(eCommander).canChangeWarPeace((TeamTypes)t, true) || GET_TEAM(eCommander).isForcePeace((TeamTypes)t))) return false;
		}
	}
	return true;
}

bool CvGame::isCrusadeWar(TeamTypes eFirst, TeamTypes eSecond) const
{
	if (m_iCrusadeRegion < 0 || eFirst < 0 || eSecond < 0 || eFirst >= MAX_TEAMS || eSecond >= MAX_TEAMS) return false;
	return (m_abCrusadeParticipants[eFirst] && m_abCrusadeTargets[eSecond]) || (m_abCrusadeParticipants[eSecond] && m_abCrusadeTargets[eFirst]);
}

bool CvGame::hasCrusadeAccess(TeamTypes eFirst, TeamTypes eSecond) const
{
	return m_iCrusadeRegion >= 0 && eFirst >= 0 && eSecond >= 0 && eFirst < MAX_TEAMS && eSecond < MAX_TEAMS && m_abCrusadeParticipants[eFirst] && m_abCrusadeParticipants[eSecond];
}

bool CvGame::isCrusadeParticipant(PlayerTypes ePlayer) const
{
	return ePlayer >= 0 && ePlayer < MAX_PLAYERS && GET_PLAYER(ePlayer).isAlive() && hasCrusadeAccess(GET_PLAYER(ePlayer).getTeam(), GET_PLAYER(ePlayer).getTeam());
}

int CvGame::getCrusadeTurnsLeft() const { return m_iCrusadeRegion < 0 ? 0 : std::max(0, m_iCrusadeEndTurn - GC.getInitCore().getGameTurn()); }
CvWString CvGame::getActiveCrusadeName() const { return getCrusadeRegionName(m_iCrusadeRegion); }
int CvGame::getCrusadePlunder(int iPlayer) const
{
	if (iPlayer >= 0 && iPlayer < MAX_PLAYERS) return m_aiCrusadePlunder[iPlayer];
	int iTotal = 0; for (int i = 0; i < MAX_PLAYERS; ++i) iTotal += m_aiCrusadePlunder[i]; return iTotal;
}

#if ARFC_ENABLE_REPORTING
void CvGame::reportApostolicState()
{
	if (!isObserverAutoPlay() || isGameMultiPlayer() || g_observerPerformance) return;
	CvCity* pRome = getPapalRome();
	ReligionTypes eChristian = (ReligionTypes)GC.getInfoTypeForString("RELIGION_CHRISTIANITY");
	BuildingTypes ePalace = (BuildingTypes)GC.getInfoTypeForString("BUILDING_APOSTOLIC_PALACE");
	int header[] = {1, m_iPapalPlayer, m_iPapalRefuser, m_iPapalRetryTurn, m_bPapalPalaceEffects,
		pRome ? pRome->getOwnerINLINE() : -1, pRome ? pRome->isHasReligion(eChristian) : 0,
		pRome ? canFoundPapacy(pRome->getOwnerINLINE()) : 0, pRome ? pRome->getNumRealBuilding(ePalace) : 0,
		m_iCrusadeRegion, m_iCrusadeEndTurn, crusadeDuration("AP_CRUSADE_BASE_TURNS"), crusadeDuration("AP_CRUSADE_INACTIVITY_TURNS")};
	std::vector<int> players, teams, pairs, ballots;
	for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
	{
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)i);
		players.push_back(i); players.push_back(kPlayer.isAlive()); players.push_back(kPlayer.getTeam());
		players.push_back(kPlayer.getStateReligion());
		players.push_back(kPlayer.getCivics((CivicOptionTypes)GC.getInfoTypeForString("CIVICOPTION_LEGAL")));
		players.push_back(kPlayer.getCivics((CivicOptionTypes)GC.getInfoTypeForString("CIVICOPTION_RELIGION")));
		players.push_back(kPlayer.getGold()); players.push_back(m_aiCrusadePlunder[i]);
		players.push_back(m_aiCrusadeRewards[i]); players.push_back(m_abCrusadeHolyStates[i]);
		players.push_back(m_aiPapalRefusalPenalties[i]);
		players.push_back(m_iPapalRefuser == NO_PLAYER ? 0 : GET_PLAYER((PlayerTypes)i).AI_getAttitudeExtra((PlayerTypes)m_iPapalRefuser));
		players.push_back(kPlayer.getNumCities());
	}
	for (int t = 0; t < MAX_TEAMS; ++t)
	{
		teams.push_back(t); teams.push_back(GET_TEAM((TeamTypes)t).isAlive());
		teams.push_back(m_abCrusadeParticipants[t]); teams.push_back(m_abCrusadeTargets[t]);
		if (m_iCrusadeRegion < 0 || !m_abCrusadeParticipants[t] || !GET_TEAM((TeamTypes)t).isAlive()) continue;
		for (int u = 0; u < MAX_TEAMS; ++u)
		{
			if (t == u || (!m_abCrusadeParticipants[u] && !m_abCrusadeTargets[u]) || !GET_TEAM((TeamTypes)u).isAlive()) continue;
			CvTeam& kTeam = GET_TEAM((TeamTypes)t);
			pairs.push_back(t); pairs.push_back(u); pairs.push_back(kTeam.isAtWar((TeamTypes)u));
			pairs.push_back(kTeam.canDeclareWar((TeamTypes)u)); pairs.push_back(kTeam.canChangeWarPeace((TeamTypes)u));
			pairs.push_back(hasCrusadeAccess((TeamTypes)t, (TeamTypes)u));
		}
	}
	int iLoop;
	for (VoteTriggeredData* pVote = m_votesTriggered.beginIter(&iLoop); pVote; pVote = m_votesTriggered.nextIter(&iLoop))
	{
		if (!isApostolicCouncil(pVote->eVoteSource)) continue;
		for (int v = 0; v < MAX_CIV_PLAYERS; ++v)
		{
			if (pVote->aiCouncilWeight[v] <= 0) continue;
			ballots.push_back(pVote->getID()); ballots.push_back(pVote->kVoteOption.eVote);
			ballots.push_back(pVote->iCouncilDeadline); ballots.push_back(v);
			ballots.push_back(pVote->aiCouncilWeight[v]); ballots.push_back(pVote->aiCouncilDelivery[v]);
			ballots.push_back(getPlayerVote((PlayerTypes)v, pVote->getID()));
		}
	}
	CyArgsList args;
	args.add(header, 13); args.add(&players[0], (int)players.size()); args.add(&teams[0], (int)teams.size());
	args.add(pairs.empty() ? (const int*)NULL : &pairs[0], (int)pairs.size());
	args.add(ballots.empty() ? (const int*)NULL : &ballots[0], (int)ballots.size());
	if (!gDLL->getPythonIFace()->callFunction("CvEventInterface", "recordApostolicState", args.makeFunctionArgs()))
		gDLL->logMsg("PythonErr.log", "Awakened RFC: apostolic state recording callback failed.", false, false);
}
#endif

void CvGame::startCrusade(int iRegion)
{
	bool abTargets[MAX_TEAMS];
	if (!canStartCrusade(iRegion) || !getCrusadeTargets(iRegion, abTargets)) return;
	VoteSourceTypes eSource = (VoteSourceTypes)GC.getInfoTypeForString("DIPLOVOTE_POPE");
	for (int t = 0; t < MAX_TEAMS; ++t)
	{
		m_abCrusadeTargets[t] = abTargets[t];
		m_abCrusadeParticipants[t] = GET_TEAM((TeamTypes)t).isAlive() && GET_TEAM((TeamTypes)t).isVotingMember(eSource);
	}
	for (int p = 0; p < MAX_TEAMS; ++p)
		if (m_abCrusadeParticipants[p])
			for (int v = 0; v < MAX_TEAMS; ++v)
				if (GET_TEAM((TeamTypes)v).isAlive() && GET_TEAM((TeamTypes)v).isVassal((TeamTypes)p)) m_abCrusadeParticipants[v] = true;
	for (int i = 0; i < MAX_PLAYERS; ++i) m_aiCrusadePlunder[i] = 0;
	for (int i = 0; i < MAX_CIV_PLAYERS; ++i) m_aiCrusadeRewards[i] = GET_PLAYER((PlayerTypes)i).isAlive() && GET_PLAYER((PlayerTypes)i).getTeam() >= 0 && m_abCrusadeParticipants[GET_PLAYER((PlayerTypes)i).getTeam()] ? 0 : -1;
	m_bCrusadePeaceOverride = true;
	for (int p = 0; p < MAX_TEAMS; ++p)
		if (m_abCrusadeParticipants[p])
			for (int q = p + 1; q < MAX_TEAMS; ++q)
				if (m_abCrusadeParticipants[q] && GET_TEAM((TeamTypes)p).isAtWar((TeamTypes)q)) GET_TEAM((TeamTypes)p).makePeace((TeamTypes)q);
	m_bCrusadePeaceOverride = false;
	m_iCrusadeRegion = iRegion;
	m_iCrusadeEndTurn = getGameTurn() + crusadeDuration("AP_CRUSADE_BASE_TURNS");
	for (int p = 0; p < MAX_TEAMS; ++p)
		if (m_abCrusadeParticipants[p] && !GET_TEAM((TeamTypes)p).isAVassal())
			for (int t = 0; t < MAX_TEAMS; ++t)
				if (m_abCrusadeTargets[t] && !GET_TEAM((TeamTypes)p).isAtWar((TeamTypes)t))
				{ GET_TEAM((TeamTypes)p).meet((TeamTypes)t, true); GET_TEAM((TeamTypes)p).declareWar((TeamTypes)t, false, WARPLAN_DOGPILE); }
	GC.getMapINLINE().verifyUnitValidPlot();
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("crusade_started", -1, m_iCrusadeRegion, m_iCrusadeEndTurn, crusadeDuration("AP_CRUSADE_BASE_TURNS"), crusadeDuration("AP_CRUSADE_INACTIVITY_TURNS"));
#endif
}

bool CvGame::isCrusadeHolyState(PlayerTypes ePlayer) const
{
	return ePlayer >= 0 && ePlayer < MAX_PLAYERS && m_abCrusadeHolyStates[ePlayer];
}

void CvGame::prepareCrusadeState(PlayerTypes ePlayer, PlayerTypes eSponsor)
{
	CvPlayer& kPlayer = GET_PLAYER(ePlayer);
	if (kPlayer.isAlive()) return;
	if (ePlayer == CRUSADER_STATE && !kPlayer.isAlive())
	{
		// This slot never belongs to the ordinary, world-wide Independent players.
		GC.getInitCore().setMinorNationCiv(ePlayer, true);
		addPlayer(ePlayer, (LeaderHeadTypes)GC.getInfoTypeForString("LEADER_INDEPENDENT"), (CivilizationTypes)GC.getInfoTypeForString("CIVILIZATION_INDEPENDENT"));
	}
	m_abCrusadeHolyStates[ePlayer] = true;
	kPlayer.setAlive(true);
	CvPlayer& kSponsor = GET_PLAYER(eSponsor);
	for (int c = 0; c < GC.getNumCivicOptionInfos(); ++c) kPlayer.setCivics((CivicOptionTypes)c, kSponsor.getCivics((CivicOptionTypes)c));
	const char* civics[] = { "CIVIC_MONARCHY", "CIVIC_THEOCRATIC_LEGITIMACY", "CIVIC_GOD_STATE" };
	for (int c = 0; c < 3; ++c)
	{
		CivicTypes eCivic = (CivicTypes)GC.getInfoTypeForString(civics[c]);
		kPlayer.setCivics((CivicOptionTypes)GC.getCivicInfo(eCivic).getCivicOptionType(), eCivic);
	}
	kPlayer.setLastStateReligion((ReligionTypes)GC.getInfoTypeForString("RELIGION_CHRISTIANITY"));
	for (int t = 0; t < GC.getNumTechInfos(); ++t)
		if (GET_TEAM(kSponsor.getTeam()).isHasTech((TechTypes)t))
			GET_TEAM(kPlayer.getTeam()).setHasTech((TechTypes)t, true, ePlayer, false, false);
	kPlayer.processCivNames();
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("crusade_state_founded", ePlayer, eSponsor, kPlayer.getStateReligion(), kPlayer.getCivics((CivicOptionTypes)GC.getInfoTypeForString("CIVICOPTION_LEGAL")), kPlayer.getCivics((CivicOptionTypes)GC.getInfoTypeForString("CIVICOPTION_RELIGION")));
#endif
	CyArgsList args;
	args.add((int)ePlayer);
	gDLL->getPythonIFace()->callFunction(PYScreensModule, "onCrusadeStateFounded", args.makeFunctionArgs());
}

void CvGame::joinCrusadeCoalition(PlayerTypes ePlayer)
{
	TeamTypes eTeam = GET_PLAYER(ePlayer).getTeam();
	if (m_iCrusadeRegion < 0 || m_abCrusadeParticipants[eTeam]) return;
	// A restored target joins the other side as a new Christian kingdom.
	m_abCrusadeTargets[eTeam] = false;
	for (int t = 0; t < MAX_TEAMS; ++t)
		if (GET_TEAM(eTeam).isVassal((TeamTypes)t)) GET_TEAM(eTeam).setVassal((TeamTypes)t, false, false);
	m_bCrusadePeaceOverride = true;
	for (int t = 0; t < MAX_TEAMS; ++t)
		if ((m_abCrusadeParticipants[t] || (isCrusadeHolyState(ePlayer) && GET_PLAYER(ePlayer).getNumCities() == 0)) && GET_TEAM(eTeam).isAtWar((TeamTypes)t)) GET_TEAM(eTeam).makePeace((TeamTypes)t);
	m_bCrusadePeaceOverride = false;
	m_abCrusadeParticipants[eTeam] = true;
	for (int p = 0; p < MAX_CIV_PLAYERS; ++p)
		if (GET_PLAYER((PlayerTypes)p).getTeam() == eTeam && m_aiCrusadeRewards[p] < 0) m_aiCrusadeRewards[p] = 0;
	for (int t = 0; t < MAX_TEAMS; ++t)
		if (m_abCrusadeTargets[t] && GET_TEAM((TeamTypes)t).isAlive() && !GET_TEAM(eTeam).isAtWar((TeamTypes)t))
		{
			// Joining a binding council war overrides the new recipient's former truce.
			GET_TEAM(eTeam).meet((TeamTypes)t, true);
			GET_TEAM(eTeam).setForcePeace((TeamTypes)t, false);
			GET_TEAM((TeamTypes)t).setForcePeace(eTeam, false);
			GET_TEAM(eTeam).declareWar((TeamTypes)t, false, WARPLAN_DOGPILE);
		}
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("crusade_joined", ePlayer, eTeam, m_iCrusadeRegion);
#endif
}

bool CvGame::isCrusadeConquest(PlayerTypes eConqueror, const CvCity& kCity) const
{
	return isCrusadeParticipant(eConqueror) && isCrusadeWar(GET_PLAYER(eConqueror).getTeam(), kCity.getTeam()) && getCrusadeRegionAt(kCity.plot()) == m_iCrusadeRegion;
}

PlayerTypes CvGame::getCrusadeCityRecipient(PlayerTypes eConqueror, const CvCity& kCity)
{
	if (!isCrusadeConquest(eConqueror, kCity)) return NO_PLAYER;
	PlayerTypes eRecipient = NO_PLAYER;

#if ARFC_ENABLE_REPORTING
	int iClaimPriority = 1;
#endif
	// Ask the same Python tables that author the historical birth/flip zones.
	CyArgsList args;
	args.add(kCity.getX_INLINE()); args.add(kCity.getY_INLINE()); args.add((int)eConqueror);
	long iClaimant = -1;
	gDLL->getPythonIFace()->callFunction(PYScreensModule, "getCrusadeFlipRecipient", args.makeFunctionArgs(), &iClaimant);
	if (iClaimant >= 0 && iClaimant < NUM_MAJOR_PLAYERS && iClaimant != eConqueror)
	{
		CvPlayer& kClaimant = GET_PLAYER((PlayerTypes)iClaimant);
		if ((!kClaimant.isAlive() && !kClaimant.isHuman() && kClaimant.getNumCities() == 0 && kClaimant.getNumUnits() == 0) ||
			(kClaimant.isAlive() && kClaimant.getStateReligion() == GC.getInfoTypeForString("RELIGION_CHRISTIANITY"))) eRecipient = (PlayerTypes)iClaimant;
	}
	if (eRecipient == NO_PLAYER)
	{

#if ARFC_ENABLE_REPORTING
		iClaimPriority = 2;
#endif
		// Eligible neighbors share a land frontier with the defeated nation in this region.
		bool abNeighbors[MAX_TEAMS]; for (int t = 0; t < MAX_TEAMS; ++t) abNeighbors[t] = false;
		for (int p = 0; p < GC.getMapINLINE().numPlotsINLINE(); ++p)
		{
			CvPlot* pPlot = GC.getMapINLINE().plotByIndexINLINE(p);
			if (getCrusadeRegionAt(pPlot) != m_iCrusadeRegion || pPlot->isWater() || pPlot->getTeam() != kCity.getTeam()) continue;
			for (int d = 0; d < NUM_CARDINALDIRECTION_TYPES; ++d)
			{
				CvPlot* pNext = plotCardinalDirection(pPlot->getX_INLINE(), pPlot->getY_INLINE(), (CardinalDirectionTypes)d);
				if (pNext && pNext->isOwned() && !pNext->isWater() && isChristianTeam(pNext->getTeam())) abNeighbors[pNext->getTeam()] = true;
			}
		}
		int iBestDistance = MAX_INT;
		for (int p = 0; p < MAX_CIV_PLAYERS; ++p)
		{
			CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)p);
			if (p == eConqueror || !kPlayer.isAlive() || kPlayer.isMinorCiv() || !abNeighbors[kPlayer.getTeam()] || kPlayer.getStateReligion() != GC.getInfoTypeForString("RELIGION_CHRISTIANITY")) continue;
			int iLoop;
			for (CvCity* pCity = kPlayer.firstCity(&iLoop); pCity; pCity = kPlayer.nextCity(&iLoop))
			{
				int iDistance = plotDistance(kCity.getX_INLINE(), kCity.getY_INLINE(), pCity->getX_INLINE(), pCity->getY_INLINE());
				if (iDistance < iBestDistance) { iBestDistance = iDistance; eRecipient = (PlayerTypes)p; }
			}
		}
	}
	if (eRecipient == NO_PLAYER)
	{
		eRecipient = (PlayerTypes)CRUSADER_STATE;
#if ARFC_ENABLE_REPORTING
		iClaimPriority = 3;
#endif
	}
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("crusade_settlement_selected", eConqueror, eRecipient, kCity.getOwnerINLINE(), kCity.getX_INLINE(), kCity.getY_INLINE(), iClaimPriority, !GET_PLAYER(eRecipient).isAlive());
#endif
	prepareCrusadeState(eRecipient, eConqueror);
	joinCrusadeCoalition(eRecipient);
	return eRecipient;
}

void CvGame::recordCrusadeActivity(TeamTypes eFirst, TeamTypes eSecond, const CvPlot* pPlot)
{
	if (!isCrusadeWar(eFirst, eSecond) || !GET_TEAM(eFirst).isAtWar(eSecond) || getCrusadeRegionAt(pPlot) != m_iCrusadeRegion) return;

#if ARFC_ENABLE_REPORTING
	const int iPreviousEnd = m_iCrusadeEndTurn;
#endif
	m_iCrusadeEndTurn = std::max(m_iCrusadeEndTurn, getGameTurn() + crusadeDuration("AP_CRUSADE_INACTIVITY_TURNS"));
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("crusade_activity", -1, eFirst, eSecond, pPlot->getX_INLINE(), pPlot->getY_INLINE(), iPreviousEnd, m_iCrusadeEndTurn, crusadeDuration("AP_CRUSADE_INACTIVITY_TURNS"));
#endif
}

void CvGame::recordCrusadePlunder(PlayerTypes ePlayer, TeamTypes eEnemy, const CvPlot* pPlot, int iGold)
{
	if (isCrusadeParticipant(ePlayer) && isCrusadeWar(GET_PLAYER(ePlayer).getTeam(), eEnemy) && getCrusadeRegionAt(pPlot) == m_iCrusadeRegion)
	{
		m_aiCrusadePlunder[ePlayer] += std::max(0, iGold);
#if ARFC_ENABLE_REPORTING
		reportApostolicMechanic("crusade_plunder", ePlayer, std::max(0, iGold), m_aiCrusadePlunder[ePlayer], eEnemy, pPlot->getX_INLINE(), pPlot->getY_INLINE());
#endif
	}
}

void CvGame::doCrusade()
{
	if (m_iCrusadeRegion < 0) return;
	bool bEnemyAlive = false, bParticipantAlive = false;
	for (int t = 0; t < MAX_TEAMS; ++t)
	{
		if (GET_TEAM((TeamTypes)t).isAlive() && m_abCrusadeTargets[t]) bEnemyAlive = true;
		if (GET_TEAM((TeamTypes)t).isAlive() && m_abCrusadeParticipants[t]) bParticipantAlive = true;
	}
	if (getGameTurn() < m_iCrusadeEndTurn && bEnemyAlive && bParticipantAlive) return;
	CvWString szRegion = getActiveCrusadeName();
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("crusade_ended", -1, m_iCrusadeRegion, m_iCrusadeEndTurn, getGameTurn() >= m_iCrusadeEndTurn ? 0 : (!bEnemyAlive ? 1 : 2));
#endif
	// Release every pair simultaneously before calling recursive vassal peace logic.
	m_iCrusadeRegion = -1;
	m_bCrusadePeaceOverride = true;
	for (int p = 0; p < MAX_TEAMS; ++p)
		if (m_abCrusadeParticipants[p])
			for (int t = 0; t < MAX_TEAMS; ++t)
				if (m_abCrusadeTargets[t] && GET_TEAM((TeamTypes)p).isAtWar((TeamTypes)t)) GET_TEAM((TeamTypes)p).makePeace((TeamTypes)t);
	m_bCrusadePeaceOverride = false;
	GC.getMapINLINE().verifyUnitValidPlot();
	for (int i = 0; i < MAX_PLAYERS; ++i)
		if (GET_PLAYER((PlayerTypes)i).isAlive() && m_abCrusadeParticipants[GET_PLAYER((PlayerTypes)i).getTeam()])
			gDLL->getInterfaceIFace()->addMessage((PlayerTypes)i, false, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_AP_CRUSADE_ENDED", szRegion.GetCString(), m_aiCrusadePlunder[i]), NULL, MESSAGE_TYPE_MAJOR_EVENT, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_WHITE"));
}

bool CvGame::canCouncilPropose(const VoteSelectionSubData& kData) const
{
	if (!isCouncilActive()) return false;
	VoteSourceTypes eSource = (VoteSourceTypes)GC.getInfoTypeForString("DIPLOVOTE_POPE");
	CvVoteInfo& kVote = GC.getVoteInfo(kData.eVote);
	if (!kVote.isVoteSourceType(eSource)) return false;
	int iMembers = 0;
	bool bUseful = false;
	bool bRelief = kData.eVote == GC.getInfoTypeForString("VOTE_AP_RELIEF");
	bool bCollege = kData.eVote == GC.getInfoTypeForString("VOTE_AP_COLLEGE");
	bool bReform = kData.eVote == GC.getInfoTypeForString("VOTE_AP_RELIGIOUS_REFORM");
	TeamTypes eTarget = kData.ePlayer == NO_PLAYER ? NO_TEAM : GET_PLAYER(kData.ePlayer).getTeam();
	if (kVote.isForceWar())
	{
		int iVoters = 0;
		for (int t = 0; t < MAX_TEAMS; ++t) if (GET_TEAM((TeamTypes)t).isAlive() && GET_TEAM((TeamTypes)t).isVotingMember(eSource)) ++iVoters;
		return iVoters >= 3 && canStartCrusade(kData.iCityId);
	}
	if (kVote.isForcePeace() && (eTarget == NO_TEAM || !GET_TEAM(eTarget).isVotingMember(eSource))) return false;
	for (int i = 0; i < MAX_CIV_TEAMS; ++i)
	{
		CvTeam& kTeam = GET_TEAM((TeamTypes)i);
		if (!kTeam.isAlive() || !kTeam.isVotingMember(eSource)) continue;
		++iMembers;
		for (int j = i + 1; j < MAX_CIV_TEAMS; ++j)
		{
			CvTeam& kOther = GET_TEAM((TeamTypes)j);
			if (!kOther.isAlive() || !kOther.isVotingMember(eSource)) continue;
			if (kVote.isOpenBorders() || kVote.isDefensivePact())
			{
				if (kTeam.isAtWar((TeamTypes)j)) return false;
				if (kVote.isOpenBorders() && !kTeam.isOpenBorders((TeamTypes)j))
				{
					bUseful = true;
				}
				if (kVote.isDefensivePact() && !kTeam.isDefensivePact((TeamTypes)j))
				{
					if (kTeam.isAVassal() || kOther.isAVassal() || !kTeam.canSignDefensivePact((TeamTypes)j)) return false;
					bUseful = true;
				}
			}
		}
		if (kVote.isForcePeace() && i != eTarget && kTeam.isAtWar(eTarget))
		{
			if (!kTeam.canChangeWarPeace(eTarget)) return false;
			bUseful = true;
		}
	}
	if (bReform)
	{
		for (int p = 0; p < MAX_CIV_PLAYERS; ++p)
			if (GET_PLAYER((PlayerTypes)p).isVotingMember(eSource) &&
				(!GET_PLAYER((PlayerTypes)p).isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_THEOCRATIC_LEGITIMACY")) || !GET_PLAYER((PlayerTypes)p).isCivic((CivicTypes)GC.getInfoTypeForString("CIVIC_GOD_STATE")))) bUseful = true;
	}
	if (bRelief || bCollege)
	{
		int iMinGold = MAX_INT, iMaxGold = 0;
		for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
		{
			CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)i);
			if (!kPlayer.isVotingMember(eSource)) continue;
			iMinGold = std::min(iMinGold, kPlayer.getGold());
			iMaxGold = std::max(iMaxGold, kPlayer.getGold());
			if (bCollege)
			{
				if (kPlayer.getGold() < 50) return false;
				TechTypes eTech = kPlayer.getCurrentResearch();
				if (eTech != NO_TECH)
					for (int j = 0; j < MAX_CIV_PLAYERS; ++j)
						if (GET_PLAYER((PlayerTypes)j).isVotingMember(eSource) && GET_TEAM(GET_PLAYER((PlayerTypes)j).getTeam()).isHasTech(eTech)) bUseful = true;
			}
		}
		if (bRelief) bUseful = iMaxGold >= 100 && iMaxGold - iMinGold >= 100;
	}
	return iMembers >= 3 && bUseful;
}

CvWString CvGame::getCouncilProposalText(const VoteSelectionSubData& kData) const
{
	CvWString szText = GC.getVoteInfo(kData.eVote).getDescription();
	if (GC.getVoteInfo(kData.eVote).isForceWar())
	{
		szText += L": " + getCrusadeRegionName(kData.iCityId);
		bool abTargets[MAX_TEAMS]; getCrusadeTargets(kData.iCityId, abTargets);
		szText += NEWLINE + gDLL->getText("TXT_KEY_AP_CRUSADE_TARGETS");
		for (int t = 0; t < MAX_TEAMS; ++t) if (abTargets[t]) szText += L" " + CvWString(GET_TEAM((TeamTypes)t).getName()) + L";";
	}
	else if (kData.ePlayer != NO_PLAYER) szText += L": " + CvWString(GET_TEAM(GET_PLAYER(kData.ePlayer).getTeam()).getName());
	if (!GC.getVoteInfo(kData.eVote).isForceWar())
		szText += NEWLINE + gDLL->getText(
		GC.getVoteInfo(kData.eVote).isForcePeace() ? "TXT_KEY_AP_TRUCE_EFFECT" :
		GC.getVoteInfo(kData.eVote).isOpenBorders() ? "TXT_KEY_AP_PILGRIM_EFFECT" :
		GC.getVoteInfo(kData.eVote).isDefensivePact() ? "TXT_KEY_AP_LEAGUE_EFFECT" :
		kData.eVote == GC.getInfoTypeForString("VOTE_AP_RELIEF") ? "TXT_KEY_AP_RELIEF_EFFECT" : kData.eVote == GC.getInfoTypeForString("VOTE_AP_RELIGIOUS_REFORM") ? "TXT_KEY_AP_REFORM_EFFECT" : "TXT_KEY_AP_COLLEGE_EFFECT");
	int iRule = GC.getVoteInfo(kData.eVote).getPopulationThreshold();
	szText += NEWLINE + gDLL->getText(iRule == 67 ? "TXT_KEY_AP_TWO_THIRDS" : iRule == 0 ? "TXT_KEY_AP_MORE_YES" : "TXT_KEY_AP_MAJORITY");
	return szText;
}

int CvGame::getCouncilVoteId() const
{
	if (!isCouncilActive()) return -1;
	int iLoop;
	for (VoteTriggeredData* pData = m_votesTriggered.beginIter(&iLoop); pData; pData = m_votesTriggered.nextIter(&iLoop))
		if (isApostolicCouncil(pData->eVoteSource)) return pData->getID();
	return -1;
}

int CvGame::getCouncilTally(int iVoteId, int iCategory, bool bNations) const
{
	VoteTriggeredData* pData = getVoteTriggered(iVoteId);
	if (!pData || !isApostolicCouncil(pData->eVoteSource)) return 0;
	int iTotal = 0;
	for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
	{
		if (pData->aiCouncilWeight[i] <= 0) continue;
		PlayerVoteTypes eVote = getPlayerVote((PlayerTypes)i, iVoteId);
		int iBucket = eVote == PLAYER_VOTE_YES ? 0 : eVote == PLAYER_VOTE_NO ? 2 : eVote == PLAYER_VOTE_ABSTAIN ? 1 : 3;
		if (iCategory == 4 || iCategory == iBucket) iTotal += bNations ? 1 : pData->aiCouncilWeight[i];
	}
	return iTotal;
}

int CvGame::getCouncilTurnsLeft(int iVoteId) const
{
	VoteTriggeredData* pData = getVoteTriggered(iVoteId);
	return pData ? std::max(0, pData->iCouncilDeadline - GC.getInitCore().getGameTurn()) : 0;
}

CvWString CvGame::getCouncilVoteText(int iVoteId) const
{
	VoteTriggeredData* pData = getVoteTriggered(iVoteId);
	return pData ? pData->kVoteOption.szText : CvWString();
}

void CvGame::doCouncilBallot(VoteTriggeredData& kData)
{
	for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
	{
		if (kData.aiCouncilWeight[i] <= 0) continue;
		CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)i);
		if (!kPlayer.isVotingMember(kData.eVoteSource) || getGameTurn() >= kData.iCouncilDeadline)
		{
			if (getPlayerVote((PlayerTypes)i, kData.getID()) == NO_PLAYER_VOTE)
				setPlayerVote((PlayerTypes)i, kData.getID(), PLAYER_VOTE_ABSTAIN);
			kData.aiCouncilDelivery[i] = -1;
			continue;
		}
		if (kData.aiCouncilDelivery[i] < 0 || getGameTurn() < kData.aiCouncilDelivery[i]) continue;
		kData.aiCouncilDelivery[i] = -1;
#if ARFC_ENABLE_REPORTING
		reportApostolicMechanic("council_delivered", i, kData.getID(), kData.aiCouncilWeight[i], kData.iCouncilDeadline);
#endif
		if (kPlayer.isHuman())
		{
			CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_DIPLOVOTE);
			if (pInfo) { pInfo->setData1(kData.getID()); gDLL->getInterfaceIFace()->addPopup(pInfo, (PlayerTypes)i); }
		}
		else castVote((PlayerTypes)i, kData.getID(), kPlayer.AI_diploVote(kData.kVoteOption, kData.eVoteSource, false));
	}
}

void CvGame::processCouncilResolution(const VoteTriggeredData& kData)
{

#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("council_resolution_applied", -1, kData.getID(), kData.kVoteOption.eVote);
#endif
	CvVoteInfo& kVote = GC.getVoteInfo(kData.kVoteOption.eVote);
	TeamTypes eTarget = kData.kVoteOption.ePlayer == NO_PLAYER ? NO_TEAM : GET_PLAYER(kData.kVoteOption.ePlayer).getTeam();
	if (kVote.isForceWar()) { startCrusade(kData.kVoteOption.iCityId); return; }
	if (kData.kVoteOption.eVote == GC.getInfoTypeForString("VOTE_AP_RELIGIOUS_REFORM"))
	{
		m_bPapalCivicOverride = true;
		for (int p = 0; p < MAX_CIV_PLAYERS; ++p)
		{
			CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)p);
			if (!kPlayer.isVotingMember(kData.eVoteSource)) continue;
			CivicTypes eTheocracy = (CivicTypes)GC.getInfoTypeForString("CIVIC_THEOCRATIC_LEGITIMACY");
			CivicTypes eHolyState = (CivicTypes)GC.getInfoTypeForString("CIVIC_GOD_STATE");
			kPlayer.setCivics((CivicOptionTypes)GC.getCivicInfo(eTheocracy).getCivicOptionType(), eTheocracy);
			kPlayer.setCivics((CivicOptionTypes)GC.getCivicInfo(eHolyState).getCivicOptionType(), eHolyState);
#if ARFC_ENABLE_REPORTING
			reportApostolicMechanic("council_reformed", p, kData.getID(), eTheocracy, eHolyState, kPlayer.getCivics((CivicOptionTypes)GC.getCivicInfo(eTheocracy).getCivicOptionType()), kPlayer.getCivics((CivicOptionTypes)GC.getCivicInfo(eHolyState).getCivicOptionType()));
#endif
		}
		m_bPapalCivicOverride = false;
		return;
	}
	for (int i = 0; i < MAX_CIV_TEAMS; ++i)
	{
		CvTeam& kTeam = GET_TEAM((TeamTypes)i);
		if (!kTeam.isVotingMember(kData.eVoteSource)) continue;
		if (kVote.isForcePeace() && i != eTarget && kTeam.isAtWar(eTarget)) kTeam.makePeace(eTarget);
		for (int j = i + 1; j < MAX_CIV_TEAMS; ++j)
		{
			if (!GET_TEAM((TeamTypes)j).isVotingMember(kData.eVoteSource)) continue;
			bool bBorders = kVote.isOpenBorders() && !kTeam.isOpenBorders((TeamTypes)j);
			bool bPact = kVote.isDefensivePact() && !kTeam.isDefensivePact((TeamTypes)j);
			if (bBorders || bPact)
			{
				// The council authorizes these treaties before their ordinary technology unlock.
				CLinkList<TradeData> ourList, theirList;
				TradeData item;
				setTradeItem(&item, bBorders ? TRADE_OPEN_BORDERS : TRADE_DEFENSIVE_PACT);
				ourList.insertAtEnd(item); theirList.insertAtEnd(item);
				implementDeal(kTeam.getLeaderID(), GET_TEAM((TeamTypes)j).getLeaderID(), &ourList, &theirList, true);
				if (bBorders) { kTeam.setTradeEmbargo((TeamTypes)j, false); GET_TEAM((TeamTypes)j).setTradeEmbargo((TeamTypes)i, false); }
			}
		}
	}
	if (kData.kVoteOption.eVote == GC.getInfoTypeForString("VOTE_AP_RELIEF"))
	{
		PlayerTypes ePoor = NO_PLAYER;
		for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
			if (GET_PLAYER((PlayerTypes)i).isVotingMember(kData.eVoteSource) && (ePoor == NO_PLAYER || GET_PLAYER((PlayerTypes)i).getGold() < GET_PLAYER(ePoor).getGold())) ePoor = (PlayerTypes)i;
		int iFund = 0;
		for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
			if (i != ePoor && GET_PLAYER((PlayerTypes)i).isVotingMember(kData.eVoteSource))
			{
				int iTithe = std::max(0, GET_PLAYER((PlayerTypes)i).getGold() / 10);
				GET_PLAYER((PlayerTypes)i).changeGold(-iTithe); iFund += iTithe;
#if ARFC_ENABLE_REPORTING
				reportApostolicMechanic("council_tithe", i, kData.getID(), -iTithe, ePoor, GET_PLAYER((PlayerTypes)i).getGold());
#endif
			}
		if (ePoor != NO_PLAYER)
		{
			GET_PLAYER(ePoor).changeGold(iFund);
#if ARFC_ENABLE_REPORTING
			reportApostolicMechanic("council_tithe", ePoor, kData.getID(), iFund, ePoor, GET_PLAYER(ePoor).getGold());
#endif
		}
	}
	if (kData.kVoteOption.eVote == GC.getInfoTypeForString("VOTE_AP_COLLEGE"))
	{
		// Determine all grants before completing any technology; no same-turn knowledge cascade.
		TechTypes aeTech[MAX_CIV_TEAMS];
		PlayerTypes aeScholar[MAX_CIV_TEAMS];
		for (int t = 0; t < MAX_CIV_TEAMS; ++t) { aeTech[t] = NO_TECH; aeScholar[t] = NO_PLAYER; }
		for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
		{
			CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)i);
			if (!kPlayer.isVotingMember(kData.eVoteSource)) continue;
			kPlayer.changeGold(-50);
#if ARFC_ENABLE_REPORTING
			reportApostolicMechanic("council_college_paid", i, kData.getID(), 50, kPlayer.getGold());
#endif
			TechTypes eTech = kPlayer.getCurrentResearch();
			if (eTech == NO_TECH || aeTech[kPlayer.getTeam()] != NO_TECH) continue;
			for (int j = 0; j < MAX_CIV_PLAYERS; ++j)
				if (GET_PLAYER((PlayerTypes)j).isVotingMember(kData.eVoteSource) && GET_TEAM(GET_PLAYER((PlayerTypes)j).getTeam()).isHasTech(eTech))
				{ aeTech[kPlayer.getTeam()] = eTech; aeScholar[kPlayer.getTeam()] = (PlayerTypes)i; break; }
		}
		for (int t = 0; t < MAX_CIV_TEAMS; ++t)
			if (aeTech[t] != NO_TECH)
			{
				int iGrant = std::max(1, GET_TEAM((TeamTypes)t).getResearchCost(aeTech[t]) / 5);
				GET_TEAM((TeamTypes)t).changeResearchProgress(aeTech[t], iGrant, aeScholar[t]);
#if ARFC_ENABLE_REPORTING
				reportApostolicMechanic("council_college_grant", aeScholar[t], kData.getID(), aeTech[t], iGrant, t);
#endif
			}
	}
}

void CvGame::rewardCrusadeCombat(CvUnit* pWinner, CvUnit* pLoser)
{
	PlayerTypes eWinner = pWinner->getOwnerINLINE();
	CvPlot* pBattlePlot = pWinner->isAttacking() ? pLoser->plot() : pWinner->plot();
	if (!isCrusadeParticipant(eWinner) || eWinner >= MAX_CIV_PLAYERS || !isCrusadeWar(pWinner->getTeam(), pLoser->getTeam()) ||
		getCrusadeRegionAt(pBattlePlot) != m_iCrusadeRegion || m_aiCrusadeRewards[eWinner] < 0 || m_aiCrusadeRewards[eWinner] >= 10 ||
		!GET_TEAM(pWinner->getTeam()).isAtWar(pLoser->getTeam()) || pWinner->getUnitInfo().isHiddenNationality() || pLoser->getUnitInfo().isHiddenNationality()) return;
	++m_aiCrusadeRewards[eWinner];
	GET_PLAYER(eWinner).changeGold(25);
	recordCrusadePlunder(eWinner, pLoser->getTeam(), pBattlePlot, 25);
#if ARFC_ENABLE_REPORTING
	reportApostolicMechanic("crusade_reward", eWinner, 25, m_aiCrusadeRewards[eWinner], pBattlePlot->getX_INLINE(), pBattlePlot->getY_INLINE());
#endif
	gDLL->getInterfaceIFace()->addMessage(eWinner, false, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_AP_CRUSADE_REWARD", 25, 10 - m_aiCrusadeRewards[eWinner]), NULL, MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"));
}

VoteSelectionData* CvGame::addVoteSelection(VoteSourceTypes eVoteSource)
{
	VoteSelectionData* pData = ((VoteSelectionData*)(m_voteSelections.add()));

	if  (NULL != pData)
	{
		pData->eVoteSource = eVoteSource;
		pData->iCouncilOwner = isApostolicCouncil(eVoteSource) && isCouncilActive() ? getApostolicPalace()->getOwnerINLINE() : NO_PLAYER;

		for (int iI = 0; iI < GC.getNumVoteInfos(); iI++)
		{
			if (GC.getVoteInfo((VoteTypes)iI).isVoteSourceType(eVoteSource))
			{
				if (isChooseElection((VoteTypes)iI))
				{
					VoteSelectionSubData kData;
					kData.eVote = (VoteTypes)iI;
					kData.iCityId = -1;
					kData.ePlayer = NO_PLAYER;
					kData.eOtherPlayer = NO_PLAYER;

					if (isApostolicCouncil(eVoteSource) && GC.getVoteInfo(kData.eVote).isForceWar())
					{
						for (int r = 0; r < getCrusadeRegionCount(); ++r)
						{
							kData.iCityId = r;
							if (canCouncilPropose(kData)) pData->aVoteOptions.push_back(kData);
						}
					}
					else if (GC.getVoteInfo(kData.eVote).isOpenBorders())
					{
						if (isValidVoteSelection(eVoteSource, kData))
						{
							kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_OPEN_BORDERS", getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource));
							pData->aVoteOptions.push_back(kData);
						}
					}
					else if (GC.getVoteInfo(kData.eVote).isDefensivePact())
					{
						if (isValidVoteSelection(eVoteSource, kData))
						{
							kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_DEFENSIVE_PACT", getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource));
							pData->aVoteOptions.push_back(kData);
						}
					}
					else if (GC.getVoteInfo(kData.eVote).isForcePeace())
					{
						for (int iTeam1 = 0; iTeam1 < MAX_CIV_TEAMS; ++iTeam1)
						{
							CvTeam& kTeam1 = GET_TEAM((TeamTypes)iTeam1);

							if (kTeam1.isAlive())
							{
								kData.ePlayer = kTeam1.getLeaderID();

								if (isValidVoteSelection(eVoteSource, kData))
								{
									//kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_FORCE_PEACE", kTeam1.getName().GetCString(), getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource)); //Rhye
									kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_FORCE_PEACE", GET_PLAYER((PlayerTypes)iTeam1).getCivilizationDescriptionKey(), getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource)); //Rhye
									pData->aVoteOptions.push_back(kData);
								}
							}
						}
					}
					else if (GC.getVoteInfo(kData.eVote).isForceNoTrade())
					{
						for (int iTeam1 = 0; iTeam1 < MAX_CIV_TEAMS; ++iTeam1)
						{
							CvTeam& kTeam1 = GET_TEAM((TeamTypes)iTeam1);

							if (kTeam1.isAlive())
							{
								kData.ePlayer = kTeam1.getLeaderID();

								if (isValidVoteSelection(eVoteSource, kData))
								{
									//kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_FORCE_NO_TRADE", kTeam1.getName().GetCString(), getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource)); //Rhye
									kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_FORCE_NO_TRADE", GET_PLAYER((PlayerTypes)iTeam1).getCivilizationDescriptionKey(), getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource)); //Rhye
									pData->aVoteOptions.push_back(kData);
								}
							}
						}
					}
					else if (GC.getVoteInfo(kData.eVote).isForceWar())
					{
						for (int iTeam1 = 0; iTeam1 < MAX_CIV_TEAMS; ++iTeam1)
						{
							CvTeam& kTeam1 = GET_TEAM((TeamTypes)iTeam1);

							if (kTeam1.isAlive())
							{
								kData.ePlayer = kTeam1.getLeaderID();

								if (isValidVoteSelection(eVoteSource, kData))
								{
									//kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_FORCE_WAR", kTeam1.getName().GetCString(), getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource)); //Rhye
									kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_FORCE_WAR", GET_PLAYER((PlayerTypes)iTeam1).getCivilizationDescriptionKey(), getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource)); //Rhye
									pData->aVoteOptions.push_back(kData);
								}
							}
						}
					}
					else if (GC.getVoteInfo(kData.eVote).isAssignCity())
					{
						for (int iPlayer1 = 0; iPlayer1 < MAX_CIV_PLAYERS; ++iPlayer1)
						{
							CvPlayer& kPlayer1 = GET_PLAYER((PlayerTypes)iPlayer1);

							int iLoop;
							for (CvCity* pLoopCity = kPlayer1.firstCity(&iLoop); NULL != pLoopCity; pLoopCity = kPlayer1.nextCity(&iLoop))
							{
								PlayerTypes eNewOwner = pLoopCity->plot()->findHighestCulturePlayer();
								if (NO_PLAYER != eNewOwner)
								{
									kData.ePlayer = (PlayerTypes)iPlayer1;
									kData.iCityId =	pLoopCity->getID();
									kData.eOtherPlayer = eNewOwner;

									if (isValidVoteSelection(eVoteSource, kData))
									{
										//kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_ASSIGN_CITY", kPlayer1.getCivilizationAdjectiveKey(), pLoopCity->getNameKey(), GET_PLAYER(eNewOwner).getNameKey(), getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource)); //Rhye
										kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_ASSIGN_CITY", kPlayer1.getCivilizationAdjectiveKey(), pLoopCity->getNameKey(), GET_PLAYER(eNewOwner).getCivilizationDescriptionKey(), getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource)); //Rhye
										pData->aVoteOptions.push_back(kData);
									}
								}
							}
						}
					}
					else
					{
						kData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_OPTION", GC.getVoteInfo(kData.eVote).getTextKeyWide(), getVoteRequired(kData.eVote, eVoteSource), countPossibleVote(kData.eVote, eVoteSource));
						if (isVotePassed(kData.eVote))
						{
							kData.szText += gDLL->getText("TXT_KEY_POPUP_PASSED");
						}

						if (canDoResolution(eVoteSource, kData))
						{
							pData->aVoteOptions.push_back(kData);
						}
					}
				}
			}
		}

		if (isApostolicCouncil(eVoteSource))
			for (int iOption = 0; iOption < (int)pData->aVoteOptions.size(); ++iOption)
				pData->aVoteOptions[iOption].szText = getCouncilProposalText(pData->aVoteOptions[iOption]);

		if (0 == pData->aVoteOptions.size())
		{
			deleteVoteSelection(pData->getID());
			pData = NULL;
		}
	}

	return pData;
}

void CvGame::deleteVoteSelection(int iID)
{
	m_voteSelections.removeAt(iID);
}

VoteTriggeredData* CvGame::getVoteTriggered(int iID) const
{
	return ((VoteTriggeredData*)(m_votesTriggered.getAt(iID)));
}

VoteTriggeredData* CvGame::addVoteTriggered(const VoteSelectionData& kData, int iChoice)
{
	if (-1 == iChoice || iChoice >= (int)kData.aVoteOptions.size())
	{
		return NULL;
	}
	
	return addVoteTriggered(kData.eVoteSource, kData.aVoteOptions[iChoice]);
}

VoteTriggeredData* CvGame::addVoteTriggered(VoteSourceTypes eVoteSource, const VoteSelectionSubData& kOptionData)
{
	VoteTriggeredData* pData = ((VoteTriggeredData*)(m_votesTriggered.add()));

	if (NULL != pData)
	{
		pData->eVoteSource = eVoteSource;
		pData->kVoteOption = kOptionData;
		pData->iCouncilDeadline = 0;
		for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
		{
			pData->aiCouncilWeight[i] = 0;
			pData->aiCouncilDelivery[i] = -1;
		}
		if (isApostolicCouncil(eVoteSource))
		{
			CvCity* pPalace = getApostolicPalace();
			if (!isCouncilActive()) { deleteVoteTriggered(pData->getID()); return NULL; }
			int iLastDelivery = getGameTurn();
			for (int i = 0; i < MAX_CIV_PLAYERS; ++i)
			{
				CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)i);
				if (!kPlayer.isVotingMember(eVoteSource)) continue;
				CvCity* pCapital = kPlayer.getCapitalCity();
				int iDistance = pCapital ? plotDistance(pCapital->getX_INLINE(), pCapital->getY_INLINE(), pPalace->getX_INLINE(), pPalace->getY_INLINE()) : 0;
				pData->aiCouncilWeight[i] = kPlayer.getVotes(kOptionData.eVote, eVoteSource);
				pData->aiCouncilDelivery[i] = getGameTurn() + 1 + std::min(2, iDistance / 12);
				iLastDelivery = std::max(iLastDelivery, pData->aiCouncilDelivery[i]);
			}
			pData->iCouncilDeadline = iLastDelivery + 3;
#if ARFC_ENABLE_REPORTING
			reportApostolicMechanic("council_opened", -1, pData->getID(), kOptionData.eVote, kOptionData.ePlayer, kOptionData.iCityId, pData->iCouncilDeadline, GC.getVoteInfo(kOptionData.eVote).getPopulationThreshold());
			for (int v = 0; v < MAX_CIV_PLAYERS; ++v)
				if (pData->aiCouncilWeight[v] > 0) reportApostolicMechanic("council_voter", v, pData->getID(), pData->aiCouncilWeight[v], pData->aiCouncilDelivery[v]);
#endif
			return pData;
		}

		for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
		{
			CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)iI);
			if (kPlayer.isVotingMember(eVoteSource))
			{
				if (kPlayer.isHuman())
				{
					CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_DIPLOVOTE);
					if (NULL != pInfo)
					{
						pInfo->setData1(pData->getID());
						gDLL->getInterfaceIFace()->addPopup(pInfo, (PlayerTypes)iI);
					}
				}
				else
				{
					castVote(((PlayerTypes)iI), pData->getID(), GET_PLAYER((PlayerTypes)iI).AI_diploVote(kOptionData, eVoteSource, false));
				}
			}
		}
	}

	return pData;
}

void CvGame::deleteVoteTriggered(int iID)
{
#if ARFC_ENABLE_REPORTING
	VoteTriggeredData* pCouncil = getVoteTriggered(iID);
	if (pCouncil && isApostolicCouncil(pCouncil->eVoteSource)) reportApostolicMechanic("council_closed", -1, iID, isCouncilActive());
#endif
	m_votesTriggered.removeAt(iID);
}

void CvGame::doVoteResults()
{
	int iLoop;
	for (VoteTriggeredData* pVoteTriggered = m_votesTriggered.beginIter(&iLoop); NULL != pVoteTriggered; pVoteTriggered = m_votesTriggered.nextIter(&iLoop))
	{
		CvWString szBuffer;
		CvWString szMessage;
		VoteTypes eVote = pVoteTriggered->kVoteOption.eVote;
		VoteSourceTypes eVoteSource = pVoteTriggered->eVoteSource;
		bool bPassed = false;

		if (isApostolicCouncil(eVoteSource))
		{
			if (!isCouncilActive()) { deleteVoteTriggered(pVoteTriggered->getID()); continue; }
			doCouncilBallot(*pVoteTriggered);
			if (getGameTurn() < pVoteTriggered->iCouncilDeadline) continue;
		}

		if (!canDoResolution(eVoteSource, pVoteTriggered->kVoteOption))
		{
			for (int iPlayer = 0; iPlayer < MAX_CIV_PLAYERS; ++iPlayer)
			{
				CvPlayer& kPlayer = GET_PLAYER((PlayerTypes) iPlayer);
				if (kPlayer.isVotingMember(eVoteSource))
				{
					CvWString szMessage;
					szMessage.Format(L"%s: %s", gDLL->getText("TXT_KEY_ELECTION_CANCELLED").GetCString(), GC.getVoteInfo(eVote).getDescription());
					gDLL->getInterfaceIFace()->addMessage((PlayerTypes)iPlayer, false, GC.getEVENT_MESSAGE_TIME(), szMessage, "AS2D_NEW_ERA", MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"));					
				}
			}
		}
		else
		{
			bool bAllVoted = true;
			for (int iJ = 0; iJ < MAX_CIV_PLAYERS; iJ++)
			{
				PlayerTypes ePlayer = (PlayerTypes) iJ;
				if (!isApostolicCouncil(eVoteSource) && GET_PLAYER(ePlayer).isVotingMember(eVoteSource))
				{
					if (getPlayerVote(ePlayer, pVoteTriggered->getID()) == NO_PLAYER_VOTE)
					{
						//give player one more turn to submit vote
						setPlayerVote(ePlayer, pVoteTriggered->getID(), NO_PLAYER_VOTE_CHECKED);
						bAllVoted = false;
						break;
					}
					else if (getPlayerVote(ePlayer, pVoteTriggered->getID()) == NO_PLAYER_VOTE_CHECKED)
					{
						//default player vote to abstain
						setPlayerVote(ePlayer, pVoteTriggered->getID(), PLAYER_VOTE_ABSTAIN);
					}
				}
			}

			if (!bAllVoted)
			{
				continue;
			}

			if (isTeamVote(eVote))
			{
				TeamTypes eTeam = findHighestVoteTeam(*pVoteTriggered);

				if (NO_TEAM != eTeam)
				{
					bPassed = countVote(*pVoteTriggered, (PlayerVoteTypes)eTeam) >= getVoteRequired(eVote, eVoteSource);
				}

				szBuffer = GC.getVoteInfo(eVote).getDescription();

				if (eTeam != NO_TEAM)
				{
					szBuffer += NEWLINE + gDLL->getText("TXT_KEY_POPUP_DIPLOMATIC_VOTING_VICTORY", GET_TEAM(eTeam).getName().GetCString(), countVote(*pVoteTriggered, (PlayerVoteTypes)eTeam), getVoteRequired(eVote, eVoteSource), countPossibleVote(eVote, eVoteSource));
				}

				for (int iI = MAX_CIV_TEAMS; iI >= 0; --iI)
				{
					for (int iJ = 0; iJ < MAX_CIV_PLAYERS; iJ++)
					{
						if (GET_PLAYER((PlayerTypes)iJ).isVotingMember(eVoteSource))
						{
							if (getPlayerVote(((PlayerTypes)iJ), pVoteTriggered->getID()) == (PlayerVoteTypes)iI)
							{
								szBuffer += NEWLINE + gDLL->getText("TXT_KEY_POPUP_VOTES_FOR", GET_PLAYER((PlayerTypes)iJ).getNameKey(), GET_TEAM((TeamTypes)iI).getName().GetCString(), GET_PLAYER((PlayerTypes)iJ).getVotes(eVote, eVoteSource));
							}
						}
					}
				}

				for (int iJ = 0; iJ < MAX_CIV_PLAYERS; iJ++)
				{
					if (GET_PLAYER((PlayerTypes)iJ).isVotingMember(eVoteSource))
					{
						if (getPlayerVote(((PlayerTypes)iJ), pVoteTriggered->getID()) == PLAYER_VOTE_ABSTAIN)
						{
							szBuffer += NEWLINE + gDLL->getText("TXT_KEY_POPUP_ABSTAINS", GET_PLAYER((PlayerTypes)iJ).getNameKey(), GET_PLAYER((PlayerTypes)iJ).getVotes(eVote, eVoteSource));
						}
					}
				}

				if (NO_TEAM != eTeam && bPassed)
				{
					setVoteOutcome(*pVoteTriggered, (PlayerVoteTypes)eTeam);
				}
				else
				{
					setVoteOutcome(*pVoteTriggered, PLAYER_VOTE_ABSTAIN);
				}
			}
			else
			{
				bPassed = countVote(*pVoteTriggered, PLAYER_VOTE_YES) >= getVoteRequired(eVote, eVoteSource);
				if (isApostolicCouncil(eVoteSource) && GC.getVoteInfo(eVote).getPopulationThreshold() == 0)
					bPassed = countVote(*pVoteTriggered, PLAYER_VOTE_YES) > countVote(*pVoteTriggered, PLAYER_VOTE_NO);

				// Defying resolution
				if (bPassed)
				{
					for (int iJ = 0; iJ < MAX_CIV_PLAYERS; iJ++)
					{
						if (!isApostolicCouncil(eVoteSource) && getPlayerVote((PlayerTypes)iJ, pVoteTriggered->getID()) == PLAYER_VOTE_NEVER)
						{
							bPassed = false;

							GET_PLAYER((PlayerTypes)iJ).setDefiedResolution(eVoteSource, pVoteTriggered->kVoteOption);
						}
					}
				}

				if (bPassed)
				{
					for (int iJ = 0; iJ < MAX_CIV_PLAYERS; iJ++)
					{
						if (GET_PLAYER((PlayerTypes)iJ).isVotingMember(eVoteSource))
						{
							if (getPlayerVote(((PlayerTypes)iJ), pVoteTriggered->getID()) == PLAYER_VOTE_YES)
							{
								GET_PLAYER((PlayerTypes)iJ).setEndorsedResolution(eVoteSource, pVoteTriggered->kVoteOption);
							}
						}
					}
				}

				if (isApostolicCouncil(eVoteSource))
				{
					const int iTotal = std::max(1, getCouncilTally(pVoteTriggered->getID(), 4, false));
					const CvWString szYes = CvWString::format(L"%d%%", (100 * getCouncilTally(pVoteTriggered->getID(), 0, false) + iTotal / 2) / iTotal);
					const CvWString szNo = CvWString::format(L"%d%%", (100 * getCouncilTally(pVoteTriggered->getID(), 2, false) + iTotal / 2) / iTotal);
					const CvWString szAbstain = CvWString::format(L"%d%%", (100 * getCouncilTally(pVoteTriggered->getID(), 1, false) + iTotal / 2) / iTotal);
					szBuffer = gDLL->getText(bPassed ? "TXT_KEY_AP_RESULT_PASS" : "TXT_KEY_AP_RESULT_FAIL", szYes.GetCString(), szNo.GetCString(), szAbstain.GetCString());
					// Keep the proposal title/target, without repeating its rules.
					szBuffer += NEWLINE + pVoteTriggered->kVoteOption.szText.substr(0, pVoteTriggered->kVoteOption.szText.find(L'\n'));
				}
				else
				szBuffer += NEWLINE + gDLL->getText((bPassed ? "TXT_KEY_POPUP_DIPLOMATIC_VOTING_SUCCEEDS" : "TXT_KEY_POPUP_DIPLOMATIC_VOTING_FAILURE"), GC.getVoteInfo(eVote).getTextKeyWide(), countVote(*pVoteTriggered, PLAYER_VOTE_YES), getVoteRequired(eVote, eVoteSource), countPossibleVote(eVote, eVoteSource));

				if (!isApostolicCouncil(eVoteSource))
				for (int iI = PLAYER_VOTE_NEVER; iI <= PLAYER_VOTE_YES; ++iI)
				{
					for (int iJ = 0; iJ < MAX_CIV_PLAYERS; iJ++)
					{
						const int iVotes = GET_PLAYER((PlayerTypes)iJ).getVotes(eVote, eVoteSource);
						if (GET_PLAYER((PlayerTypes)iJ).isVotingMember(eVoteSource))
						{
							if (getPlayerVote(((PlayerTypes)iJ), pVoteTriggered->getID()) == (PlayerVoteTypes)iI)
							{
								switch ((PlayerVoteTypes)iI)
								{
								case PLAYER_VOTE_ABSTAIN:
									szBuffer += NEWLINE + gDLL->getText("TXT_KEY_POPUP_ABSTAINS", GET_PLAYER((PlayerTypes)iJ).getNameKey(), iVotes);
									break;
								case PLAYER_VOTE_NEVER:
									szBuffer += NEWLINE + gDLL->getText("TXT_KEY_POPUP_VOTES_YES_NO", GET_PLAYER((PlayerTypes)iJ).getNameKey(), L"TXT_KEY_POPUP_VOTE_NEVER", iVotes);
									break;
								case PLAYER_VOTE_NO:
									szBuffer += NEWLINE + gDLL->getText("TXT_KEY_POPUP_VOTES_YES_NO", GET_PLAYER((PlayerTypes)iJ).getNameKey(), L"TXT_KEY_POPUP_NO", iVotes);
									break;
								case PLAYER_VOTE_YES:
									szBuffer += NEWLINE + gDLL->getText("TXT_KEY_POPUP_VOTES_YES_NO", GET_PLAYER((PlayerTypes)iJ).getNameKey(), L"TXT_KEY_POPUP_YES", iVotes);
									break;
								default:
									FAssert(false);
									break;
								}
							}
						}
					}
				}


#if ARFC_ENABLE_REPORTING
				if (isApostolicCouncil(eVoteSource)) reportApostolicMechanic("council_result", -1, pVoteTriggered->getID(), eVote, bPassed, getCouncilTally(pVoteTriggered->getID(), 0, false), getCouncilTally(pVoteTriggered->getID(), 2, false), getCouncilTally(pVoteTriggered->getID(), 1, false), getCouncilTally(pVoteTriggered->getID(), 4, false), getVoteRequired(eVote, eVoteSource));
#endif
				setVoteOutcome(*pVoteTriggered, bPassed ? PLAYER_VOTE_YES : PLAYER_VOTE_NO);
			}

			for (int iI = 0; iI < MAX_CIV_PLAYERS; iI++)
			{
				CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)iI);
				if (kPlayer.isHuman())
				{
					bool bShow = isApostolicCouncil(eVoteSource) ?
						pVoteTriggered->aiCouncilWeight[iI] > 0 : kPlayer.isVotingMember(pVoteTriggered->eVoteSource);

					if (bShow)
					{
						CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_TEXT);
						if (NULL != pInfo)
						{
							pInfo->setText(szBuffer);
							gDLL->getInterfaceIFace()->addPopup(pInfo, (PlayerTypes)iI);
						}
					}

					if (!bShow)
					{
						if (iI == pVoteTriggered->kVoteOption.ePlayer && GET_PLAYER(pVoteTriggered->kVoteOption.ePlayer).isVotingMember(pVoteTriggered->eVoteSource))
						{
							bShow = true;
						}
					}

					if (!bShow)
					{
						if (iI == pVoteTriggered->kVoteOption.eOtherPlayer && GET_PLAYER(pVoteTriggered->kVoteOption.eOtherPlayer).isVotingMember(pVoteTriggered->eVoteSource))
						{
							bShow = true;
						}
					}

					if (bShow && bPassed)
					{
						CvWString szMessage = gDLL->getText("TXT_KEY_VOTE_RESULTS", GC.getVoteSourceInfo(eVoteSource).getTextKeyWide(), pVoteTriggered->kVoteOption.szText.GetCString());
						gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getEVENT_MESSAGE_TIME(), szMessage, "AS2D_NEW_ERA", MESSAGE_TYPE_MINOR_EVENT, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_HIGHLIGHT_TEXT"));
					}

				}
			}
		}

		if (!bPassed && GC.getVoteInfo(eVote).isSecretaryGeneral())
		{
			setSecretaryGeneralTimer(eVoteSource, 0);
		}

		deleteVoteTriggered(pVoteTriggered->getID());
	}
}

void CvGame::doVoteSelection()
{
	for (int iI = 0; iI < GC.getNumVoteSourceInfos(); ++iI)
	{
		VoteSourceTypes eVoteSource = (VoteSourceTypes)iI;
		if (isApostolicCouncil(eVoteSource))
		{
			if (m_iPapalFirstCouncilTurn >= 0 && getGameTurn() < m_iPapalFirstCouncilTurn) continue;
			if (getCouncilVoteId() >= 0) continue;
			bool bPending = false;
			int iSelection;
			for (VoteSelectionData* pSelection = m_voteSelections.beginIter(&iSelection); pSelection; pSelection = m_voteSelections.nextIter(&iSelection))
				if (pSelection->eVoteSource == eVoteSource) bPending = true;
			if (bPending) continue;
		}

		if (isDiploVote(eVoteSource))
		{
			if (getVoteTimer(eVoteSource) > 0)
			{
				changeVoteTimer(eVoteSource, -1);
			}
			else
			{
				setVoteTimer(eVoteSource, ((isApostolicCouncil(eVoteSource) ? 30 : GC.getVoteSourceInfo(eVoteSource).getVoteInterval()) * GC.getGameSpeedInfo(getGameSpeedType()).getVictoryDelayPercent()) / 100);

				for (int iTeam1 = 0; iTeam1 < MAX_CIV_TEAMS; ++iTeam1)
				{
					CvTeam& kTeam1 = GET_TEAM((TeamTypes)iTeam1);

					if (kTeam1.isAlive() && kTeam1.isVotingMember(eVoteSource))
					{
						for (int iTeam2 = iTeam1 + 1; iTeam2 < MAX_CIV_TEAMS; ++iTeam2)
						{
							CvTeam& kTeam2 = GET_TEAM((TeamTypes)iTeam2);

							if (kTeam2.isAlive() && kTeam2.isVotingMember(eVoteSource))
							{
								kTeam1.meet((TeamTypes)iTeam2, true);
							}
						}
					}
				}

				TeamTypes eSecretaryGeneral = getSecretaryGeneral(eVoteSource);
				PlayerTypes eSecretaryPlayer;

				if (eSecretaryGeneral != NO_TEAM)
				{
					eSecretaryPlayer = isApostolicCouncil(eVoteSource) ? getApostolicPalace()->getOwnerINLINE() : GET_TEAM(eSecretaryGeneral).getSecretaryID();
				}
				else
				{
					eSecretaryPlayer = NO_PLAYER;
				}

				bool bSecretaryGeneralVote = false;
				if (!isApostolicCouncil(eVoteSource) && canHaveSecretaryGeneral(eVoteSource))
				{
					if (getSecretaryGeneralTimer(eVoteSource) > 0)
					{
						changeSecretaryGeneralTimer(eVoteSource, -1);
					}
					else
					{
						setSecretaryGeneralTimer(eVoteSource, GC.getDefineINT("DIPLO_VOTE_SECRETARY_GENERAL_INTERVAL"));

						for (int iJ = 0; iJ < GC.getNumVoteInfos(); iJ++)
						{
							if (GC.getVoteInfo((VoteTypes)iJ).isSecretaryGeneral() && GC.getVoteInfo((VoteTypes)iJ).isVoteSourceType(iI))
							{
								VoteSelectionSubData kOptionData;
								kOptionData.iCityId = -1;
								kOptionData.ePlayer = NO_PLAYER;
								kOptionData.eVote = (VoteTypes)iJ;
								kOptionData.szText = gDLL->getText("TXT_KEY_POPUP_ELECTION_OPTION", GC.getVoteInfo((VoteTypes)iJ).getTextKeyWide(), getVoteRequired((VoteTypes)iJ, eVoteSource), countPossibleVote((VoteTypes)iJ, eVoteSource));
								addVoteTriggered(eVoteSource, kOptionData);
								bSecretaryGeneralVote = true;
								break;
							}
						}
					}
				}

				if (!bSecretaryGeneralVote && eSecretaryGeneral != NO_TEAM && eSecretaryPlayer != NO_PLAYER)
				{
					VoteSelectionData* pData = addVoteSelection(eVoteSource);
					if (NULL != pData)
					{
						if (GET_PLAYER(eSecretaryPlayer).isHuman())
						{
							CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_CHOOSEELECTION);
							if (NULL != pInfo)
							{
								pInfo->setData1(pData->getID());
								gDLL->getInterfaceIFace()->addPopup(pInfo, eSecretaryPlayer);
							}
						}
						else
						{
							setVoteChosen(GET_TEAM(eSecretaryGeneral).AI_chooseElection(*pData), pData->getID());
						}
					}
					else
					{
						setVoteTimer(eVoteSource, 0);
					}
				}
			}
		}
	}
}

bool CvGame::isEventActive(EventTriggerTypes eTrigger) const
{
	for (std::vector<EventTriggerTypes>::const_iterator it = m_aeInactiveTriggers.begin(); it != m_aeInactiveTriggers.end(); ++it)
	{
		if (*it == eTrigger)
		{
			return false;
		}
	}

	return true;
}

void CvGame::initEvents()
{
	for (int iTrigger = 0; iTrigger < GC.getNumEventTriggerInfos(); ++iTrigger)
	{
		if (isOption(GAMEOPTION_NO_EVENTS) || getSorenRandNum(100, "Event Active?") >= GC.getEventTriggerInfo((EventTriggerTypes)iTrigger).getPercentGamesActive())
		{
			m_aeInactiveTriggers.push_back((EventTriggerTypes)iTrigger);
		}
	}
}

bool CvGame::isCivEverActive(CivilizationTypes eCivilization) const
{
	for (int iPlayer = 0; iPlayer < MAX_PLAYERS; ++iPlayer)
	{
		CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iPlayer);
		if (kLoopPlayer.isEverAlive())
		{
			if (kLoopPlayer.getCivilizationType() == eCivilization)
			{
				return true;
			}
		}
	}

	return false;
}

bool CvGame::isLeaderEverActive(LeaderHeadTypes eLeader) const
{
	for (int iPlayer = 0; iPlayer < MAX_PLAYERS; ++iPlayer)
	{
		CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iPlayer);
		if (kLoopPlayer.isEverAlive())
		{
			if (kLoopPlayer.getLeaderType() == eLeader)
			{
				return true;
			}
		}
	}

	return false;
}

bool CvGame::isUnitEverActive(UnitTypes eUnit) const
{
	for (int iCiv = 0; iCiv < GC.getNumCivilizationInfos(); ++iCiv)
	{
		if (isCivEverActive((CivilizationTypes)iCiv))
		{
			if (eUnit == GC.getCivilizationInfo((CivilizationTypes)iCiv).getCivilizationUnits(GC.getUnitInfo(eUnit).getUnitClassType()))
			{
				return true;
			}
		}
	}

	return false;
}

bool CvGame::isBuildingEverActive(BuildingTypes eBuilding) const
{
	for (int iCiv = 0; iCiv < GC.getNumCivilizationInfos(); ++iCiv)
	{
		if (isCivEverActive((CivilizationTypes)iCiv))
		{
			if (eBuilding == GC.getCivilizationInfo((CivilizationTypes)iCiv).getCivilizationBuildings(GC.getBuildingInfo(eBuilding).getBuildingClassType()))
			{
				return true;
			}
		}
	}

	return false;
}

void CvGame::processBuilding(BuildingTypes eBuilding, int iChange)
{
	for (int iI = 0; iI < GC.getNumVoteSourceInfos(); ++iI)
	{
		if (GC.getBuildingInfo(eBuilding).getVoteSourceType() == (VoteSourceTypes)iI)
		{
			changeDiploVote((VoteSourceTypes)iI, iChange);
		}
	}
}

bool CvGame::pythonIsBonusIgnoreLatitudes() const
{
	long lResult = -1;
	if (gDLL->getPythonIFace()->callFunction(gDLL->getPythonIFace()->getMapScriptModule(), "isBonusIgnoreLatitude", NULL, &lResult))
	{
		if (!gDLL->getPythonIFace()->pythonUsingDefaultImpl() && lResult != -1)
		{
			return (lResult != 0);
		}
	}

	return false;
}

//Rhye - start (RFCMP)
int CvGame::getFakeRandNum(int iMax)
{
	return (getSorenRand().getSeed() % (getGameTurn() + 100) ) % iMax;
}

int CvGame::getFakeBigRandNum(int iMax)
{
	return (getSorenRand().getSeed() % (getGameTurn() + 10000) ) % iMax;
}
//Rhye - end

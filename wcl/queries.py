"""Reusable GraphQL query strings."""

TOP_PARSES_QUERY = """
query TopParses($encounterID: Int!, $specName: String!, $className: String!, $metric: CharacterRankingMetricType, $difficulty: Int, $page: Int) {
  worldData {
    encounter(id: $encounterID) {
      name
      characterRankings(
        specName: $specName
        className: $className
        metric: $metric
        difficulty: $difficulty
        page: $page
        leaderboard: LogsOnly
      )
    }
  }
}
"""

PLAYER_DETAILS_QUERY = """
query PlayerDetails($reportCode: String!, $fightID: Int!) {
  reportData {
    report(code: $reportCode) {
      playerDetails(fightIDs: [$fightID], includeCombatantInfo: true)
      fights(fightIDs: [$fightID]) {
        id
        startTime
        endTime
        encounterID
        kill
      }
      masterData {
        actors {
          id
          name
          type
          subType
        }
        abilities {
          gameID
          name
          type
          icon
        }
      }
    }
  }
}
"""

ENCOUNTER_LIST_QUERY = """
query {
  worldData {
    expansions {
      id
      name
      zones {
        id
        name
        difficulties {
          id
          name
        }
        encounters {
          id
          name
        }
      }
    }
  }
}
"""

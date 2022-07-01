-- See Zulip discussion on the faction order, mapping factions isn't trivial:
--  https://faforever.zulipchat.com/#narrow/stream/203478-general/topic/Faction.20Order/near/235006069
-- I went with Sheikah's approach:
--  > You can continue this discussion but for the client I will just use the
--  > four basic ones and everything else will be considered random as that is
--  > the only consistent thing
CREATE FUNCTION faf_ladder_1v1.FACTION_NAME(id INT64)
  RETURNS STRING
  AS (CASE id
    WHEN 1 THEN "UEF"
    WHEN 2 THEN "Aeon"
    WHEN 3 THEN "Cybran"
    WHEN 4 THEN "Seraphim"
    ELSE "Other"
  END);

-- Copied from Konstantin Kalinovsky's parser.
-- See https://github.com/FAForever/faf-scfa-replay-parser/blob/9d0cb7cb4bb0cf6d8be44e5c1ea4bc357aa9a0c5/replay_parser/constants.py#L197
CREATE FUNCTION faf_ladder_1v1.COMMAND_NAME(id INT64)
  RETURNS STRING
  AS (CASE id
    WHEN 0 THEN "NONE"
    WHEN 1 THEN "Stop"
    WHEN 2 THEN "Move"
    WHEN 3 THEN "Dive"
    WHEN 4 THEN "FormMove"
    WHEN 5 THEN "BuildSiloTactical"
    WHEN 6 THEN "BuildSiloNuke"
    WHEN 7 THEN "BuildFactory"
    WHEN 8 THEN "BuildMobile"
    WHEN 9 THEN "BuildAssist"
    WHEN 10 THEN "Attack"
    WHEN 11 THEN "FormAttack"
    WHEN 12 THEN "Nuke"
    WHEN 13 THEN "Tactical"
    WHEN 14 THEN "Teleport"
    WHEN 15 THEN "Guard"
    WHEN 16 THEN "Patrol"
    WHEN 17 THEN "Ferry"
    WHEN 18 THEN "FormPatrol"
    WHEN 19 THEN "Reclaim"
    WHEN 20 THEN "Repair"
    WHEN 21 THEN "Capture"
    WHEN 22 THEN "TransportLoadUnits"
    WHEN 23 THEN "TransportReverseLoadUnits"
    WHEN 24 THEN "TransportUnloadUnits"
    WHEN 25 THEN "TransportUnloadSpecificUnits"
    WHEN 26 THEN "DetachFromTransport"
    WHEN 27 THEN "Upgrade"
    WHEN 28 THEN "Script"
    WHEN 29 THEN "AssistCommander"
    WHEN 30 THEN "KillSelf"
    WHEN 31 THEN "DestroySelf"
    WHEN 32 THEN "Sacrifice"
    WHEN 33 THEN "Pause"
    WHEN 34 THEN "OverCharge"
    WHEN 35 THEN "AggressiveMove"
    WHEN 36 THEN "FormAggressiveMove"
    WHEN 37 THEN "AssistMove"
    WHEN 38 THEN "SpecialAction"
    WHEN 39 THEN "Dock"
    ELSE "UNKNOWN"
  END);

CREATE FUNCTION faf_ladder_1v1.GEOMETRY_NAME(width INT64, height INT64)
  RETURNS STRING
  AS (CASE (width, height)
    WHEN (512, 512) THEN "10x10"
    WHEN (1024, 1024) THEN "20x20"
    WHEN (256, 256) THEN "5x5"
    WHEN (2048, 2048) THEN "40x40"
    WHEN (4096, 4096) THEN "80x80"
    WHEN (1024, 512) THEN "10x5"
    ELSE FORMAT("raw-%dx%d", width, height)
  END);

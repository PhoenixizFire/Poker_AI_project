USE pokeraiproject;

DROP TABLE Table6Phase1Action;

CREATE TABLE IF NOT EXISTS Table6Phase1Action (
    gameID VARCHAR(12) PRIMARY KEY NOT NULL,
    gamePot VARCHAR(10),
    Player1Action VARCHAR(20),
    Player1Bet VARCHAR(20),
    Player1Money VARCHAR(20),
    Player1Status VARCHAR(20),
    Player1Card1Value VARCHAR(2),
    Player1Card1Figure VARCHAR(20),
    Player1Card2Value VARCHAR(2),
    Player1Card2Figure VARCHAR(20),
    Player2Action VARCHAR(20),
    Player2Bet VARCHAR(20),
    Player2Money VARCHAR(20),
    Player2Status VARCHAR(20),
    Player2Card1Value VARCHAR(2),
    Player2Card1Figure VARCHAR(20),
    Player2Card2Value VARCHAR(2),
    Player2Card2Figure VARCHAR(20),
    Player3Action VARCHAR(20),
    Player3Bet VARCHAR(20),
    Player3Money VARCHAR(20),
    Player3Status VARCHAR(20),
    Player3Card1Value VARCHAR(2),
    Player3Card1Figure VARCHAR(20),
    Player3Card2Value VARCHAR(2),
    Player3Card2Figure VARCHAR(20),
    Player4Action VARCHAR(20),
    Player4Bet VARCHAR(20),
    Player4Money VARCHAR(20),
    Player4Status VARCHAR(20),
    Player4Card1Value VARCHAR(2),
    Player4Card1Figure VARCHAR(20),
    Player4Card2Value VARCHAR(2),
    Player4Card2Figure VARCHAR(20),
    Player5Action VARCHAR(20),
    Player5Bet VARCHAR(20),
    Player5Money VARCHAR(20),
    Player5Status VARCHAR(20),
    Player5Card1Value VARCHAR(2),
    Player5Card1Figure VARCHAR(20),
    Player5Card2Value VARCHAR(2),
    Player5Card2Figure VARCHAR(20),
    Player6Action VARCHAR(20),
    Player6Bet VARCHAR(20),
    Player6Money VARCHAR(20),
    Player6Status VARCHAR(20),
    Player6Card1Value VARCHAR(2),
    Player6Card1Figure VARCHAR(20),
    Player6Card2Value VARCHAR(2),
    Player6Card2Figure VARCHAR(20)
);

DROP TABLE Table6Phase2Action;

CREATE TABLE IF NOT EXISTS Table6Phase2Action (
    gameID VARCHAR(12) PRIMARY KEY NOT NULL,
    gamePot VARCHAR(10),
    gameCard1Value VARCHAR(2),
    gameCard1Figure VARCHAR(20),
    gameCard2Value VARCHAR(2),
    gameCard2Figure VARCHAR(20),
    gameCard3Value VARCHAR(2),
    gameCard3Figure VARCHAR(20),
    Player1Action VARCHAR(20),
    Player1Bet VARCHAR(20),
    Player1Money VARCHAR(20),
    Player1Status VARCHAR(20),
    Player1Card1Value VARCHAR(2),
    Player1Card1Figure VARCHAR(20),
    Player1Card2Value VARCHAR(2),
    Player1Card2Figure VARCHAR(20),
    Player2Action VARCHAR(20),
    Player2Bet VARCHAR(20),
    Player2Money VARCHAR(20),
    Player2Status VARCHAR(20),
    Player2Card1Value VARCHAR(2),
    Player2Card1Figure VARCHAR(20),
    Player2Card2Value VARCHAR(2),
    Player2Card2Figure VARCHAR(20),
    Player3Action VARCHAR(20),
    Player3Bet VARCHAR(20),
    Player3Money VARCHAR(20),
    Player3Status VARCHAR(20),
    Player3Card1Value VARCHAR(2),
    Player3Card1Figure VARCHAR(20),
    Player3Card2Value VARCHAR(2),
    Player3Card2Figure VARCHAR(20),
    Player4Action VARCHAR(20),
    Player4Bet VARCHAR(20),
    Player4Money VARCHAR(20),
    Player4Status VARCHAR(20),
    Player4Card1Value VARCHAR(2),
    Player4Card1Figure VARCHAR(20),
    Player4Card2Value VARCHAR(2),
    Player4Card2Figure VARCHAR(20),
    Player5Action VARCHAR(20),
    Player5Bet VARCHAR(20),
    Player5Money VARCHAR(20),
    Player5Status VARCHAR(20),
    Player5Card1Value VARCHAR(2),
    Player5Card1Figure VARCHAR(20),
    Player5Card2Value VARCHAR(2),
    Player5Card2Figure VARCHAR(20),
    Player6Action VARCHAR(20),
    Player6Bet VARCHAR(20),
    Player6Money VARCHAR(20),
    Player6Status VARCHAR(20),
    Player6Card1Value VARCHAR(2),
    Player6Card1Figure VARCHAR(20),
    Player6Card2Value VARCHAR(2),
    Player6Card2Figure VARCHAR(20)
);

DROP TABLE Table6Phase3Action;

CREATE TABLE IF NOT EXISTS Table6Phase3Action (
    gameID VARCHAR(12) PRIMARY KEY NOT NULL,
    gamePot VARCHAR(10),
    gameCard4Value VARCHAR(2),
    gameCard4Figure VARCHAR(20),
    Player1Action VARCHAR(20),
    Player1Bet VARCHAR(20),
    Player1Money VARCHAR(20),
    Player1Status VARCHAR(20),
    Player1Card1Value VARCHAR(2),
    Player1Card1Figure VARCHAR(20),
    Player1Card2Value VARCHAR(2),
    Player1Card2Figure VARCHAR(20),
    Player2Action VARCHAR(20),
    Player2Bet VARCHAR(20),
    Player2Money VARCHAR(20),
    Player2Status VARCHAR(20),
    Player2Card1Value VARCHAR(2),
    Player2Card1Figure VARCHAR(20),
    Player2Card2Value VARCHAR(2),
    Player2Card2Figure VARCHAR(20),
    Player3Action VARCHAR(20),
    Player3Bet VARCHAR(20),
    Player3Money VARCHAR(20),
    Player3Status VARCHAR(20),
    Player3Card1Value VARCHAR(2),
    Player3Card1Figure VARCHAR(20),
    Player3Card2Value VARCHAR(2),
    Player3Card2Figure VARCHAR(20),
    Player4Action VARCHAR(20),
    Player4Bet VARCHAR(20),
    Player4Money VARCHAR(20),
    Player4Status VARCHAR(20),
    Player4Card1Value VARCHAR(2),
    Player4Card1Figure VARCHAR(20),
    Player4Card2Value VARCHAR(2),
    Player4Card2Figure VARCHAR(20),
    Player5Action VARCHAR(20),
    Player5Bet VARCHAR(20),
    Player5Money VARCHAR(20),
    Player5Status VARCHAR(20),
    Player5Card1Value VARCHAR(2),
    Player5Card1Figure VARCHAR(20),
    Player5Card2Value VARCHAR(2),
    Player5Card2Figure VARCHAR(20),
    Player6Action VARCHAR(20),
    Player6Bet VARCHAR(20),
    Player6Money VARCHAR(20),
    Player6Status VARCHAR(20),
    Player6Card1Value VARCHAR(2),
    Player6Card1Figure VARCHAR(20),
    Player6Card2Value VARCHAR(2),
    Player6Card2Figure VARCHAR(20)
);

DROP TABLE Table6Phase4Action;

CREATE TABLE IF NOT EXISTS Table6Phase4Action (
    gameID VARCHAR(12) PRIMARY KEY NOT NULL,
    gamePot VARCHAR(10),
    gameCard5Value VARCHAR(2),
    gameCard5Figure VARCHAR(20),
    Player1Action VARCHAR(20),
    Player1Bet VARCHAR(20),
    Player1Money VARCHAR(20),
    Player1Status VARCHAR(20),
    Player1Card1Value VARCHAR(2),
    Player1Card1Figure VARCHAR(20),
    Player1Card2Value VARCHAR(2),
    Player1Card2Figure VARCHAR(20),
    Player2Action VARCHAR(20),
    Player2Bet VARCHAR(20),
    Player2Money VARCHAR(20),
    Player2Status VARCHAR(20),
    Player2Card1Value VARCHAR(2),
    Player2Card1Figure VARCHAR(20),
    Player2Card2Value VARCHAR(2),
    Player2Card2Figure VARCHAR(20),
    Player3Action VARCHAR(20),
    Player3Bet VARCHAR(20),
    Player3Money VARCHAR(20),
    Player3Status VARCHAR(20),
    Player3Card1Value VARCHAR(2),
    Player3Card1Figure VARCHAR(20),
    Player3Card2Value VARCHAR(2),
    Player3Card2Figure VARCHAR(20),
    Player4Action VARCHAR(20),
    Player4Bet VARCHAR(20),
    Player4Money VARCHAR(20),
    Player4Status VARCHAR(20),
    Player4Card1Value VARCHAR(2),
    Player4Card1Figure VARCHAR(20),
    Player4Card2Value VARCHAR(2),
    Player4Card2Figure VARCHAR(20),
    Player5Action VARCHAR(20),
    Player5Bet VARCHAR(20),
    Player5Money VARCHAR(20),
    Player5Status VARCHAR(20),
    Player5Card1Value VARCHAR(2),
    Player5Card1Figure VARCHAR(20),
    Player5Card2Value VARCHAR(2),
    Player5Card2Figure VARCHAR(20),
    Player6Action VARCHAR(20),
    Player6Bet VARCHAR(20),
    Player6Money VARCHAR(20),
    Player6Status VARCHAR(20),
    Player6Card1Value VARCHAR(2),
    Player6Card1Figure VARCHAR(20),
    Player6Card2Value VARCHAR(2),
    Player6Card2Figure VARCHAR(20)
);

DROP TABLE Table6Result;

CREATE TABLE IF NOT EXISTS Table6Result (
    gameID VARCHAR(12) PRIMARY KEY NOT NULL,
    Player1Outcome VARCHAR(20),
    Player2Outcome VARCHAR(20),
    Player3Outcome VARCHAR(20),
    Player4Outcome VARCHAR(20),
    Player5Outcome VARCHAR(20),
    Player6Outcome VARCHAR(20)
);


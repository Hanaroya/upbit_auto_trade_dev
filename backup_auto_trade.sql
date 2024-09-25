-- --------------------------------------------------------
-- 호스트:                          127.0.0.1
-- 서버 버전:                        8.0.33 - MySQL Community Server - GPL
-- 서버 OS:                        Win64
-- HeidiSQL 버전:                  12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- coin-auto-trade 데이터베이스 구조 내보내기
DROP DATABASE IF EXISTS `coin-auto-trade`;
CREATE DATABASE IF NOT EXISTS `coin-auto-trade` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `coin-auto-trade`;

-- 테이블 coin-auto-trade.coin_holding 구조 내보내기
DROP TABLE IF EXISTS `coin_holding`;
CREATE TABLE IF NOT EXISTS `coin_holding` (
  `c_code` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `r_holding` tinyint NOT NULL DEFAULT (0),
  `c_rank` int NOT NULL DEFAULT (0),
  `position` varchar(40) NOT NULL,
  `simul_chk` tinyint(1) NOT NULL DEFAULT (0),
  `hold` tinyint(1) DEFAULT NULL,
  `current_price` float DEFAULT NULL,
  `current_percent` float DEFAULT NULL,
  `price_b` float DEFAULT NULL,
  `rsi` float DEFAULT NULL,
  `deposit` float DEFAULT NULL,
  `user_call` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`c_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 테이블 데이터 coin-auto-trade.coin_holding:~0 rows (대략적) 내보내기
DELETE FROM `coin_holding`;

-- 테이블 coin-auto-trade.coin_list 구조 내보내기
DROP TABLE IF EXISTS `coin_list`;
CREATE TABLE IF NOT EXISTS `coin_list` (
  `c_code` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `position` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `record` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `rsi` float DEFAULT NULL,
  `hold` tinyint(1) DEFAULT NULL,
  `r_holding` tinyint(1) DEFAULT NULL,
  `buy_uuid` varchar(40) DEFAULT NULL,
  `volume` double DEFAULT NULL,
  `price_b` float DEFAULT NULL,
  `percent` float DEFAULT NULL,
  `deposit` float DEFAULT NULL,
  PRIMARY KEY (`c_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 테이블 데이터 coin-auto-trade.coin_list:~0 rows (대략적) 내보내기
DELETE FROM `coin_list`;

-- 테이블 coin-auto-trade.coin_list_selling 구조 내보내기
DROP TABLE IF EXISTS `coin_list_selling`;
CREATE TABLE IF NOT EXISTS `coin_list_selling` (
  `c_code` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `position` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `record` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `rsi` float DEFAULT NULL,
  `hold` tinyint(1) DEFAULT NULL,
  `sell_uuid` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '실제 판매 확인용',
  `buy_uuid` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '실제 구매 확인용',
  `r_holding` tinyint DEFAULT NULL COMMENT '실거래 보유중',
  `volume` double DEFAULT NULL,
  `price_b` float DEFAULT NULL,
  `percent` float DEFAULT NULL,
  `deposit` float DEFAULT NULL,
  PRIMARY KEY (`c_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;

-- 테이블 데이터 coin-auto-trade.coin_list_selling:~0 rows (대략적) 내보내기
DELETE FROM `coin_list_selling`;

-- 테이블 coin-auto-trade.deposit_holding 구조 내보내기
DROP TABLE IF EXISTS `deposit_holding`;
CREATE TABLE IF NOT EXISTS `deposit_holding` (
  `coin_key` int unsigned NOT NULL,
  `dp_am` float DEFAULT NULL,
  `sv_am` float DEFAULT NULL,
  `or_am` float DEFAULT NULL,
  `pr_am` float DEFAULT NULL,
  PRIMARY KEY (`coin_key`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 테이블 데이터 coin-auto-trade.deposit_holding:~2 rows (대략적) 내보내기
DELETE FROM `deposit_holding`;
INSERT INTO `deposit_holding` (`coin_key`, `dp_am`, `sv_am`, `or_am`, `pr_am`) VALUES
	(1, 880000, 120000, 1000000, 0),
	(2, NULL, NULL, NULL, NULL);

-- 테이블 coin-auto-trade.trade_history 구조 내보내기
DROP TABLE IF EXISTS `trade_history`;
CREATE TABLE IF NOT EXISTS `trade_history` (
  `c_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `c_rank` int DEFAULT NULL,
  `current_price` float DEFAULT NULL,
  `percent` float DEFAULT NULL,
  `date_time` datetime DEFAULT NULL,
  `c_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `reason` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `deposit` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 테이블 데이터 coin-auto-trade.trade_history:~0 rows (대략적) 내보내기
DELETE FROM `trade_history`;

-- 테이블 coin-auto-trade.trade_result_history 구조 내보내기
DROP TABLE IF EXISTS `trade_result_history`;
CREATE TABLE IF NOT EXISTS `trade_result_history` (
  `date_time` datetime DEFAULT NULL,
  `total_investment` float DEFAULT NULL,
  `sv_am` int DEFAULT NULL,
  `income` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 테이블 데이터 coin-auto-trade.trade_result_history:~4 rows (대략적) 내보내기
DELETE FROM `trade_result_history`;
INSERT INTO `trade_result_history` (`date_time`, `total_investment`, `sv_am`, `income`) VALUES
	('2024-09-12 14:55:19', 1000000, 120000, 0),
	('2024-09-17 19:00:00', 1000000, 120000, 0),
	('2024-09-19 17:47:53', 1000000, 120000, 0),
	('2024-09-24 07:07:35', 1000000, 120000, 0);

-- 테이블 coin-auto-trade.trade_rules 구조 내보내기
DROP TABLE IF EXISTS `trade_rules`;
CREATE TABLE IF NOT EXISTS `trade_rules` (
  `coin_key` int NOT NULL DEFAULT '0',
  `b_limit` tinyint(1) DEFAULT '0',
  `b_limit1` tinyint(1) DEFAULT '0',
  `b_limit2` tinyint(1) DEFAULT '0',
  `b_limit3` tinyint(1) DEFAULT '0',
  `b_limit4` tinyint(1) DEFAULT '0',
  `b_limit5` tinyint(1) DEFAULT '0',
  `s_limit` tinyint(1) DEFAULT '0',
  `simulate` tinyint(1) DEFAULT '0',
  `terminate` tinyint(1) DEFAULT NULL,
  `running` tinyint(1) DEFAULT NULL,
  `daily_report_chk` tinyint(1) DEFAULT NULL,
  `30min_update_chk` tinyint DEFAULT NULL,
  `hourly_report_chk` tinyint DEFAULT NULL,
  PRIMARY KEY (`coin_key`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 테이블 데이터 coin-auto-trade.trade_rules:~1 rows (대략적) 내보내기
DELETE FROM `trade_rules`;
INSERT INTO `trade_rules` (`coin_key`, `b_limit`, `b_limit1`, `b_limit2`, `b_limit3`, `b_limit4`, `b_limit5`, `s_limit`, `simulate`, `terminate`, `running`, `daily_report_chk`, `30min_update_chk`, `hourly_report_chk`) VALUES
	(1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0);

-- 테이블 coin-auto-trade.trading_list 구조 내보내기
DROP TABLE IF EXISTS `trading_list`;
CREATE TABLE IF NOT EXISTS `trading_list` (
  `coin_key` int NOT NULL,
  `total_ubmi` float DEFAULT NULL,
  `change_ubmi_now` float DEFAULT NULL,
  `change_ubmi_before` float DEFAULT NULL,
  `fear_greed` float DEFAULT NULL,
  `coin_pl` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `t_list1` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `t_list_chk1` tinyint(1) DEFAULT NULL,
  `t_list2` text,
  `t_list_chk2` tinyint(1) DEFAULT NULL,
  `t_list3` text,
  `t_list_chk3` tinyint(1) DEFAULT NULL,
  `t_list4` text,
  `t_list_chk4` tinyint(1) DEFAULT NULL,
  `t_list5` text,
  `t_list_chk5` tinyint(1) DEFAULT NULL,
  `sell_list_chk` tinyint DEFAULT NULL,
  `buy_chk` tinyint DEFAULT NULL,
  `sell_chk` tinyint DEFAULT NULL,
  PRIMARY KEY (`coin_key`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 테이블 데이터 coin-auto-trade.trading_list:~1 rows (대략적) 내보내기
DELETE FROM `trading_list`;
INSERT INTO `trading_list` (`coin_key`, `total_ubmi`, `change_ubmi_now`, `change_ubmi_before`, `fear_greed`, `coin_pl`, `t_list1`, `t_list_chk1`, `t_list2`, `t_list_chk2`, `t_list3`, `t_list_chk3`, `t_list4`, `t_list_chk4`, `t_list5`, `t_list_chk5`, `sell_list_chk`, `buy_chk`, `sell_chk`) VALUES
	(1, 12702.9, 70.53, 70.53, 54.93, '["KRW-IQ", "KRW-NEAR", "KRW-GRT", "KRW-GMT", "KRW-PYTH", "KRW-ONDO", "KRW-STX", "KRW-HBAR", "KRW-AAVE", "KRW-ZETA", "KRW-ANKR", "KRW-IMX", "KRW-STMX", "KRW-UPP", "KRW-CHZ", "KRW-BLUR", "KRW-IOST", "KRW-TON", "KRW-CELO", "KRW-AHT", "KRW-TT", "KRW-FCT2", "KRW-GAME2", "KRW-SC", "KRW-BIGTIME", "KRW-MASK", "KRW-POLYX", "KRW-BEAM", "KRW-MBL", "KRW-LOOM", "KRW-UXLINK", "KRW-ZRX", "KRW-AXS", "KRW-ICX", "KRW-BAT", "KRW-LSK", "KRW-MVL", "KRW-STRIKE", "KRW-ADA", "KRW-ZIL", "KRW-LINK", "KRW-1INCH", "KRW-WAXP", "KRW-GAS", "KRW-ETH", "KRW-ENS", "KRW-AKT", "KRW-SBD", "KRW-SXP", "KRW-DOT", "KRW-IOTA", "KRW-QTUM", "KRW-STRAX", "KRW-EGLD", "KRW-CBK", "KRW-STG", "KRW-T", "KRW-GLM", "KRW-FLOW", "KRW-MINA", "KRW-HIFI", "KRW-MTL", "KRW-HIVE", "KRW-ONT", "KRW-DKA", "KRW-META", "KRW-BORA", "KRW-SNT", "KRW-ALGO", "KRW-GRS", "KRW-VET", "KRW-KNC", "KRW-STORJ", "KRW-POWR", "KRW-DOGE", "KRW-ETC", "KRW-STEEM", "KRW-KAVA", "KRW-ELF", "KRW-POL", "KRW-QKC", "KRW-WAVES", "KRW-XEC", "KRW-BSV", "KRW-CTC", "KRW-EOS", "KRW-G", "KRW-XEM", "KRW-JST", "KRW-TRX", "KRW-CRO", "KRW-XTZ", "KRW-XLM", "KRW-HUNT", "KRW-MED", "KRW-MANA", "KRW-ASTR", "KRW-MLK", "KRW-BLAST", "KRW-HPO", "KRW-USDC", "KRW-BTG", "KRW-AUCTION", "KRW-USDT", "KRW-AVAX", "KRW-STPT", "KRW-MNT", "KRW-SAND", "KRW-XRP", "KRW-ID", "KRW-ATOM", "KRW-BTC", "KRW-THETA", "KRW-SHIB", "KRW-ARB", "KRW-TFUEL", "KRW-BCH", "KRW-SOL", "KRW-ATH", "KRW-SEI", "KRW-NEO", "KRW-PUNDIX", "KRW-ORBS", "KRW-BTT", "KRW-CVC", "KRW-ONG", "KRW-APT", "KRW-AERGO", "KRW-JUP", "KRW-CKB", "KRW-SUI", "KRW-PENDLE", "KRW-AQT", "KRW-ZRO", "KRW-TAIKO", "KRW-ARDR", "KRW-ARK", "KRW-MOC"]', '{"list": [123, 113, 82, 0, 12, 23, 129, 19, 28, 29, 22, 13]}', 0, '{"list": [20, 21, 137, 36, 98, 27, 52, 118, 122, 10, 30, 105]}', 0, '{"list": [16, 80, 94, 135, 14, 56, 86, 9, 74, 24, 87, 108]}', 0, '{"list": [7, 2, 119, 42, 3, 39, 15, 67, 65, 70, 136, 103]}', 0, '{"list": [64, 90, 115, 127, 130, 124, 5, 96, 99, 89, 88, 6]}', 0, NULL, NULL, NULL);

-- 테이블 coin-auto-trade.trading_log 구조 내보내기
DROP TABLE IF EXISTS `trading_log`;
CREATE TABLE IF NOT EXISTS `trading_log` (
  `c_code` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `position` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `record` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `report` text,
  `dt_log` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT=' print 함수 대신 모든 결과를 여기로 전달';

-- 테이블 데이터 coin-auto-trade.trading_log:~0 rows (대략적) 내보내기
DELETE FROM `trading_log`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

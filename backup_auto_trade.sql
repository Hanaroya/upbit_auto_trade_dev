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

-- 테이블 coin-auto-trade.blacklist 구조 내보내기
DROP TABLE IF EXISTS `blacklist`;
CREATE TABLE IF NOT EXISTS `blacklist` (
  `c_code` char(50) DEFAULT NULL,
  `date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 테이블 데이터 coin-auto-trade.blacklist:~0 rows (대략적) 내보내기
DELETE FROM `blacklist`;

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

-- 테이블 데이터 coin-auto-trade.coin_holding:~14 rows (대략적) 내보내기
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

-- 테이블 데이터 coin-auto-trade.coin_list:~139 rows (대략적) 내보내기
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

-- 테이블 데이터 coin-auto-trade.coin_list_selling:~14 rows (대략적) 내보내기
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

-- 테이블 데이터 coin-auto-trade.deposit_holding:~1 rows (대략적) 내보내기
DELETE FROM `deposit_holding`;
INSERT INTO `deposit_holding` (`coin_key`, `dp_am`, `sv_am`, `or_am`, `pr_am`) VALUES
	(1, 880968, 120142, 1001110, 0),
	(2, 0, 0, 1111.35, 0);

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

-- 테이블 데이터 coin-auto-trade.trade_history:~328 rows (대략적) 내보내기
DELETE FROM `trade_history`;

-- 테이블 coin-auto-trade.trade_result_history 구조 내보내기
DROP TABLE IF EXISTS `trade_result_history`;
CREATE TABLE IF NOT EXISTS `trade_result_history` (
  `date_time` datetime DEFAULT NULL,
  `total_investment` float DEFAULT NULL,
  `sv_am` int DEFAULT NULL,
  `income` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 테이블 데이터 coin-auto-trade.trade_result_history:~2 rows (대략적) 내보내기
DELETE FROM `trade_result_history`;
INSERT INTO `trade_result_history` (`date_time`, `total_investment`, `sv_am`, `income`) VALUES
	('2024-09-30 21:56:00', 1000000, 120000, 687),
	('2024-10-02 19:00:00', 1000000, 120000, 1106);

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
	(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

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
	(1, 12105, -44.53, -65.38, 44.91, '["KRW-GRS", "KRW-APT", "KRW-SXP", "KRW-XEC", "KRW-STX", "KRW-TON", "KRW-ETC", "KRW-SUI", "KRW-USDT", "KRW-USDC", "KRW-PUNDIX", "KRW-DKA", "KRW-BTT", "KRW-BTG", "KRW-THETA", "KRW-TRX", "KRW-MANA", "KRW-BTC", "KRW-BSV", "KRW-PENDLE", "KRW-SC", "KRW-BAT", "KRW-SNT", "KRW-WAXP", "KRW-JST", "KRW-IOST", "KRW-QKC", "KRW-CHZ", "KRW-ETH", "KRW-GRT", "KRW-POL", "KRW-STPT", "KRW-STEEM", "KRW-LSK", "KRW-HUNT", "KRW-BCH", "KRW-AHT", "KRW-MASK", "KRW-EGLD", "KRW-T", "KRW-DOT", "KRW-TFUEL", "KRW-MOC", "KRW-EOS", "KRW-CTC", "KRW-META", "KRW-MVL", "KRW-ALGO", "KRW-STG", "KRW-VET", "KRW-KNC", "KRW-G", "KRW-MLK", "KRW-ELF", "KRW-ICX", "KRW-TT", "KRW-ARB", "KRW-SAND", "KRW-POLYX", "KRW-AUCTION", "KRW-LINK", "KRW-ONT", "KRW-GAME2", "KRW-ENS", "KRW-STRAX", "KRW-XEM", "KRW-AXS", "KRW-NEO", "KRW-PYTH", "KRW-BORA", "KRW-STRIKE", "KRW-ASTR", "KRW-MBL", "KRW-ARDR", "KRW-HBAR", "KRW-XLM", "KRW-DOGE", "KRW-CRO", "KRW-MTL", "KRW-1INCH", "KRW-BIGTIME", "KRW-GMT", "KRW-AAVE", "KRW-MNT", "KRW-ZIL", "KRW-MED", "KRW-POWR", "KRW-STMX", "KRW-XTZ", "KRW-ONG", "KRW-GLM", "KRW-AKT", "KRW-ID", "KRW-GAS", "KRW-ADA", "KRW-SHIB", "KRW-FLOW", "KRW-HIVE", "KRW-BLAST", "KRW-CBK", "KRW-AQT", "KRW-FCT2", "KRW-STORJ", "KRW-IOTA", "KRW-ATH", "KRW-ANKR", "KRW-ATOM", "KRW-HIFI", "KRW-SOL", "KRW-SBD", "KRW-HPO", "KRW-IMX", "KRW-KAVA", "KRW-QTUM", "KRW-LOOM", "KRW-CKB", "KRW-NEAR", "KRW-AVAX", "KRW-JUP", "KRW-UXLINK", "KRW-ARK", "KRW-ORBS", "KRW-W", "KRW-ONDO", "KRW-IQ", "KRW-ZETA", "KRW-XRP", "KRW-ZRX", "KRW-SEI", "KRW-ZRO", "KRW-AERGO", "KRW-BLUR", "KRW-WAVES", "KRW-CELO", "KRW-UPP", "KRW-MINA", "KRW-TAIKO", "KRW-CVC", "KRW-BEAM"]', '{"list": [126, 122, 17, 7, 128, 95, 119, 8, 108, 4, 3, 28]}', 0, '{"list": [137, 121, 76, 115, 2, 116, 138, 125, 131, 1, 123, 80]}', 0, '{"list": [120, 133, 37, 129, 12, 68, 6, 64, 136, 42, 19, 41]}', 0, '{"list": [18, 132, 0, 112, 135, 94, 67, 82, 73, 117, 98, 30]}', 0, '{"list": [35, 101, 104, 81, 15, 56, 87, 90, 63, 58, 23, 114]}', 0, 0, 0, 0);

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

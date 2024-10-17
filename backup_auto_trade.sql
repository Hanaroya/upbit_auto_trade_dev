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
  `c_code` char(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `date` datetime DEFAULT NULL,
  `timeout` int DEFAULT NULL,
  `out_count` int DEFAULT NULL,
  PRIMARY KEY (`c_code`)
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

-- 테이블 데이터 coin-auto-trade.coin_holding:~3 rows (대략적) 내보내기
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

-- 테이블 데이터 coin-auto-trade.coin_list:~140 rows (대략적) 내보내기
DELETE FROM `coin_list`;

-- 테이블 coin-auto-trade.coin_list_selling 구조 내보내기
DROP TABLE IF EXISTS `coin_list_selling`;
CREATE TABLE IF NOT EXISTS `coin_list_selling` (
  `c_code` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `position` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `record` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `rsi` float DEFAULT NULL,
  `percent` float DEFAULT NULL,
  `hold` tinyint(1) DEFAULT NULL,
  `sell_uuid` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '실제 판매 확인용',
  `buy_uuid` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '실제 구매 확인용',
  `r_holding` tinyint DEFAULT NULL COMMENT '실거래 보유중',
  `volume` double DEFAULT NULL,
  `price_b` float DEFAULT NULL,
  `deposit` float DEFAULT NULL,
  PRIMARY KEY (`c_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;

-- 테이블 데이터 coin-auto-trade.coin_list_selling:~3 rows (대략적) 내보내기
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
	(1, 883377, 120640, 1005260, 0),
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

-- 테이블 데이터 coin-auto-trade.trade_history:~73 rows (대략적) 내보내기
DELETE FROM `trade_history`;

-- 테이블 coin-auto-trade.trade_result_history 구조 내보내기
DROP TABLE IF EXISTS `trade_result_history`;
CREATE TABLE IF NOT EXISTS `trade_result_history` (
  `date_time` datetime DEFAULT NULL,
  `total_investment` float DEFAULT NULL,
  `sv_am` int DEFAULT NULL,
  `income` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 테이블 데이터 coin-auto-trade.trade_result_history:~8 rows (대략적) 내보내기
DELETE FROM `trade_result_history`;
INSERT INTO `trade_result_history` (`date_time`, `total_investment`, `sv_am`, `income`) VALUES
	('2024-09-30 21:56:00', 1000000, 120000, 687),
	('2024-10-02 19:00:00', 1000000, 120000, 1106),
	('2024-10-09 20:03:40', 1000000, 120000, 0),
	('2024-10-10 21:09:20', 1000000, 120000, -6325),
	('2024-10-11 19:08:20', 1000000, 120000, 1279),
	('2024-10-15 19:00:00', 1000000, 120000, 0),
	('2024-10-16 08:05:58', 1000000, 120000, 3836),
	('2024-10-16 19:10:20', 1003840, 120463, 1425);

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
	(1, 13415.6, -26.95, -43.07, 57.48, '["KRW-IQ", "KRW-INJ", "KRW-SNT", "KRW-AHT", "KRW-LOOM", "KRW-UPP", "KRW-BIGTIME", "KRW-XRP", "KRW-META", "KRW-MBL", "KRW-MVL", "KRW-AAVE", "KRW-JST", "KRW-BLUR", "KRW-ETH", "KRW-USDT", "KRW-DKA", "KRW-USDC", "KRW-TT", "KRW-GAME2", "KRW-TRX", "KRW-BTG", "KRW-BCH", "KRW-MED", "KRW-XLM", "KRW-BTC", "KRW-APT", "KRW-STMX", "KRW-XTZ", "KRW-ORBS", "KRW-MNT", "KRW-SUI", "KRW-HUNT", "KRW-QKC", "KRW-SBD", "KRW-MLK", "KRW-SOL", "KRW-CRO", "KRW-POL", "KRW-BTT", "KRW-SXP", "KRW-LSK", "KRW-BLAST", "KRW-AQT", "KRW-MASK", "KRW-TFUEL", "KRW-ZIL", "KRW-PUNDIX", "KRW-GLM", "KRW-MINA", "KRW-T", "KRW-HPO", "KRW-ETC", "KRW-BAT", "KRW-IOST", "KRW-CKB", "KRW-ENS", "KRW-CBK", "KRW-BSV", "KRW-ADA", "KRW-AVAX", "KRW-SEI", "KRW-EOS", "KRW-ONDO", "KRW-AUCTION", "KRW-HIVE", "KRW-SC", "KRW-MOC", "KRW-ARB", "KRW-CTC", "KRW-LINK", "KRW-ZRX", "KRW-ELF", "KRW-BORA", "KRW-GRT", "KRW-AXS", "KRW-ANKR", "KRW-CELO", "KRW-ALGO", "KRW-WAVES", "KRW-IOTA", "KRW-IMX", "KRW-FCT2", "KRW-ATOM", "KRW-DOT", "KRW-VET", "KRW-G", "KRW-QTUM", "KRW-EGLD", "KRW-MANA", "KRW-BEAM", "KRW-ICX", "KRW-ID", "KRW-ASTR", "KRW-FLOW", "KRW-DOGE", "KRW-AERGO", "KRW-NEO", "KRW-1INCH", "KRW-STRAX", "KRW-STPT", "KRW-THETA", "KRW-HIFI", "KRW-AKT", "KRW-SAND", "KRW-STRIKE", "KRW-XEM", "KRW-ONG", "KRW-STEEM", "KRW-ATH", "KRW-WAXP", "KRW-KNC", "KRW-STX", "KRW-XEC", "KRW-PENDLE", "KRW-NEAR", "KRW-GRS", "KRW-UXLINK", "KRW-ONT", "KRW-TON", "KRW-GMT", "KRW-MTL", "KRW-SHIB", "KRW-POLYX", "KRW-ZRO", "KRW-ZETA", "KRW-TAIKO", "KRW-STG", "KRW-POWR", "KRW-W", "KRW-JUP", "KRW-CVC", "KRW-CHZ", "KRW-HBAR", "KRW-KAVA", "KRW-GAS", "KRW-PYTH", "KRW-ARDR", "KRW-ARK", "KRW-STORJ", "KRW-CARV"]', '{"list": [25, 138, 7, 31, 95, 122, 0, 1, 140, 15, 139, 36]}', 0, '{"list": [112, 14, 61, 5, 4, 135, 6, 117, 132, 22, 115, 58]}', 0, '{"list": [26, 13, 21, 137, 63, 2, 125, 131, 129, 136, 113, 124]}', 0, '{"list": [29, 77, 49, 52, 3, 59, 55, 126, 38, 60, 107, 68]}', 0, '{"list": [133, 27, 82, 66, 8, 39, 20, 114, 16, 74, 109, 103]}', 0, 0, 0, 0);

-- 테이블 coin-auto-trade.trading_log 구조 내보내기
DROP TABLE IF EXISTS `trading_log`;
CREATE TABLE IF NOT EXISTS `trading_log` (
  `c_code` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `position` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `record` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `report` text,
  `dt_log` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT=' print 함수 대신 모든 결과를 여기로 전달';

-- 테이블 데이터 coin-auto-trade.trading_log:~192 rows (대략적) 내보내기
DELETE FROM `trading_log`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

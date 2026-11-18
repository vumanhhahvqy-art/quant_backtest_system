# Manifest hồ sơ kiểm toán

Snapshot UTC: 2026-11-17T09:33:31.742505+00:00; commit nền: `7af3b774b1721e091e2527a00563912255d44702`.

54 source, 54 bản sao byte-for-byte khớp; không có source bị bỏ sót hoặc lặp toàn văn.
SHA256 dùng bytes gốc, bảo toàn CRLF/BOM/trailing newline; nội dung block không thêm line numbers.

| File nguồn | Gói chứa toàn văn | Bytes | Dòng | SHA256 |
|---|---|---|---|---|
| .clinerules/01-project.md | 00B_PROJECT_RULES.md | 4394 | 148 | bab5fd7c934dbafc9b5fdd01ca99decb1dee343bfb80d2adf5bfbaeeac7df7ff |
| .clinerules/02-architecture.md | 00B_PROJECT_RULES.md | 8448 | 379 | 661c1dabf0208252c754728ea662a541453c4eda95ca3e1951aeabb2545ef5e8 |
| .clinerules/03-backtest-rules.md | 00B_PROJECT_RULES.md | 9474 | 378 | 05b47622a0f36bf43e937e53c1cadbd5d8c69e7f8fd3441e32e7fe3adff050b0 |
| .clinerules/04-coding-standards.md | 00B_PROJECT_RULES.md | 8057 | 354 | abbb028656ba48d3cd76c260c90292d02e19dc0ef49a07a78796cef19c76e586 |
| .gitignore | 00_PROJECT_OVERVIEW.md | 579 | 37 | be0d2f36340d702fbc07a7480d90153cf4d8c90953753674dec5e1799759b325 |
| .vscode/settings.json | 00_PROJECT_OVERVIEW.md | 68 | 3 | b3f38d5469db454a51c0c705ae9160a4e133df1f23c19f7086cce7169a544aa9 |
| README.md | 00_PROJECT_OVERVIEW.md | 5310 | 116 | 9c4081319675161b9283a6d61e08a4e92711c6818bd5c050112b22e68d6677f8 |
| benchmark_engine.py | 04_STRATEGIES_AUDIT.md | 3683 | 82 | cd05b5f735df19d816d32ad9e155bdd8331194ec52d73322d4844f5cc1b21e34 |
| configs/config.yaml | 02_DATA_AUDIT.md | 624 | 14 | 2cc5306a3d1c2936082d016558d8f08b7b79f90386ed41487382b73cd4036a53 |
| configs/data_pipeline.yaml | 02_DATA_AUDIT.md | 323 | 8 | 29aaaf776797b23b37c8fcd1bb8aca53eaf4c9888770d26b77aae23a150111cc |
| core/BACKTEST_ENGINE.md | 01_CORE_AUDIT.md | 14292 | 207 | 48963307de96476d1010ef50a79881391177bdde159ced0a6341991f871dc672 |
| core/__init__.py | 01_CORE_AUDIT.md | 0 | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core/causality.py | 06_VALIDATION_AUDIT.md | 1945 | 40 | fe7fa61ef157e6ec5df20932e917380a144dba932e42c5f14f03af4c14b82afc |
| core/cost_model.py | 01_CORE_AUDIT.md | 2746 | 57 | b8e12db3ae11c56f9ca9c0521e8ab24d6bda4595c4f9b24db07149f72a1178fc |
| core/data_loader.py | 02_DATA_AUDIT.md | 10823 | 239 | 82973a19cc0fca229accd3517c331d99983cdf076b4d786f4f2a14c28e793d11 |
| core/data_manager.py | 02_DATA_AUDIT.md | 112 | 1 | df7b63964ada00c56fca5f763a24e2152a282649a57871e8c1f397423be43e8c |
| core/data_validator.py | 02_DATA_AUDIT.md | 10363 | 199 | 99d379352c38a509765d0e0fc7a73b77508bde9e2946cb3f7b467aad749449c4 |
| core/engine.py | 01_CORE_AUDIT.md | 12934 | 229 | b2e35f439025d9b932dec9a8a94c00e94b3317df965c282cfe4c6335bc46880b |
| core/execution.py | 01_CORE_AUDIT.md | 1401 | 37 | fdd5262964943c0b9e817f3857b088af6b675dc0026f5dd853d10c0bcff1628e |
| core/metrics.py | 06_VALIDATION_AUDIT.md | 93 | 1 | 1bda281456baf27201e2cc167010aa01b2feb35b5f107b0ed2be9e80b0412317 |
| core/models.py | 01_CORE_AUDIT.md | 5714 | 153 | 81c2b36789871376a1e39f68dc0980f1bb676be14c153fa2bee2f3f1b14df79d |
| core/portfolio.py | 01_CORE_AUDIT.md | 3954 | 70 | 7f5c0d55cd3b454fdf1e34101b40cbcf398de0a06d1ef1104c93860cf01c3d24 |
| data/metadata/datasets.json | 02_DATA_AUDIT.md | 1718 | 31 | 7e628dc9a7cfa90a71b287434e71f36d7d03aef4b4350f5de38853cd46dc5ffc |
| data/metadata/metadata_template.yaml | 02_DATA_AUDIT.md | 994 | 24 | d3609fd78dd00c8e74da0b2400063c58517f20beedeb8504f96412596afeb80c |
| data/metadata/symbols.json | 02_DATA_AUDIT.md | 893 | 32 | c02e3acb85953637e0eb377b2a017512746a1b28ad135f6b30884a4fd41eadff |
| indicators/INDICATORS.md | 03_INDICATORS_AUDIT.md | 15348 | 199 | 2461a9e586cc8c01194587f73e396e14c90ec579e5900556dafb38bf69103ff8 |
| indicators/__init__.py | 03_INDICATORS_AUDIT.md | 385 | 11 | 976c65f4c859b580916dacd575b21a7f2d7a394c4aea601e48b3d7a3828cb724 |
| indicators/_utils.py | 03_INDICATORS_AUDIT.md | 2419 | 56 | 0697022c77e7e6bccf1b63c1a4304c8a6b58ccc26358b1c206a5615f47693f05 |
| indicators/custom_indicators.py | 03_INDICATORS_AUDIT.md | 108 | 1 | 8193340316dd56eddd778f4f064544457598c97763381ce1141383635dcfd6a5 |
| indicators/market_structure.py | 03D_INDICATORS_STRUCTURE.md | 10174 | 189 | fb8b1238e509b3684c6f929dd6a965201603e76f957a28cea335b9d4efdf7180 |
| indicators/momentum.py | 03B_INDICATORS_MOMENTUM.md | 5488 | 128 | d205f9adb507e4b063492c2580a5fc4c29dde4f6e6324d1b5af515c7f90ec904 |
| indicators/moving_averages.py | 03A_INDICATORS_TREND.md | 2280 | 65 | e18a302d8c0a87b203d2c9ac56e9051938625cd5910eb1bb4085c086024aaebf |
| indicators/price_action.py | 03E_INDICATORS_PRICE_ACTION.md | 7330 | 142 | 3ba1ca770837f91bed1408ef5cf31f8abfd38b298c33cccf3e7069fff8bd8c0d |
| indicators/sessions.py | 03F_INDICATORS_SESSIONS_VOLUME.md | 10890 | 210 | 2bc30841a895d433b25813297e9aef7c343ce4a2a21024f4948ea14672794a16 |
| indicators/trend.py | 03A_INDICATORS_TREND.md | 8659 | 167 | 53860ac974b483809e3bd1b0c18e540f141666e29ac1ffe3e53b88b9505decff |
| indicators/volatility.py | 03C_INDICATORS_VOLATILITY.md | 5186 | 106 | 737f53fcbdf0644ec645bfe2562669b9e21a9ad1a149062698f17f654e59bbd4 |
| inspect_data.py | 02_DATA_AUDIT.md | 6421 | 122 | 9987700c7c745d27fc1e16ddc710ec2c0f4742c0e6b27743fe03a46e426d49f8 |
| inspect_indicators.py | 03G_INDICATORS_DIAGNOSTICS.md | 7359 | 124 | c033894bee8c3be300fb31f3d574daa94f513d212a1fa3f98d8dfbd785536125 |
| pyproject.toml | 00_PROJECT_OVERVIEW.md | 726 | 29 | 8cc6c6a19958d3254d69361dccd1fdc92ae470f259e1ff88fe3a4f88235cb892 |
| run_backtest.py | 00_PROJECT_OVERVIEW.md | 288 | 9 | 42967f49c9b2640f54332b14bdee8232711a1117218e81023bd17425434a3f28 |
| strategies/__init__.py | 04_STRATEGIES_AUDIT.md | 0 | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| strategies/base_strategy.py | 01_CORE_AUDIT.md | 1769 | 33 | f476111d945bf4d50ad9ccac81b8f03f07d822c62aa87a8994a835e24af2eaad |
| strategies/first_strategy.py | 04_STRATEGIES_AUDIT.md | 133 | 2 | f1ebc4e02a4e55fc7f5db75e83a740b0980384b09784f7216a3b3518fc6d963c |
| tests/test_backtest_models.py | 05A_TESTS_MODELS_COSTS_PORTFOLIO.md | 2891 | 78 | ecd084d2ca4cb1da762d3010473885569fb81f607b00e2d20c7a01d4a37b481f |
| tests/test_cost_model.py | 05A_TESTS_MODELS_COSTS_PORTFOLIO.md | 1330 | 33 | 71936c1a12518f645480ba31b6305091dfada45543440c1f374610485bb38e41 |
| tests/test_data_loader.py | 05C_TESTS_DATA.md | 6705 | 154 | 3cc3774987d25aa1206b5c88e5603a7b743ef0a3d7a5915b8cb32edb6084930f |
| tests/test_data_validator.py | 05C_TESTS_DATA.md | 4612 | 102 | a34c3fbebae332d582b4152c7ebc7a4e5530845e12d809381d790d953153d1a5 |
| tests/test_engine.py | 05B_TESTS_ENGINE_REVIEW.md | 13110 | 273 | dea2360ce920923cd6479da095fcd004997301d06c99ae903d0f13e635e84ad7 |
| tests/test_environment.py | 05E_TESTS_ENVIRONMENT.md | 759 | 22 | 880c51eaf356d9be1c8f8157a2f2ecc2335b64f98cc9fc9b2d1b7ab4b164aa6f |
| tests/test_execution.py | 05A_TESTS_MODELS_COSTS_PORTFOLIO.md | 1343 | 30 | c30cbef36f5ff8f6227437f1e706d8319c45a3ba31bd9982a350bfa0161c5a60 |
| tests/test_indicators.py | 05D_TESTS_INDICATORS.md | 20622 | 384 | 9765c5229bf05059e452eec9cb6a592fca2f6277c80783666e84adbc84dd5188 |
| tests/test_intraday_gaps.py | 05C_TESTS_DATA.md | 4582 | 90 | 519e1e8d0a60fa174af2b8280b3921750fd0b1bd29fd3f0b3f154323ca5a0c57 |
| tests/test_portfolio.py | 05A_TESTS_MODELS_COSTS_PORTFOLIO.md | 1985 | 46 | d0b990946cfdb10b8d56acf7b6f705ec4e74c7965c5f78386385b9a158dafa4c |
| tests/test_stage4_review.py | 05B_TESTS_ENGINE_REVIEW.md | 3401 | 78 | 611717b706e4ff73e8a6f2a15e3d217aff2c1327517e4caf2ea0e60c081d6d0c |


## Kích thước và SHA256 từng gói

Không tự hash MANIFEST để tránh tham chiếu vòng.

| Gói | Bytes | SHA256 |
|---|---|---|
| 00A_SOURCE_INVENTORY.md | 27531 | 79b52b2dfd86cb78efc1234623bd060442a5bcb3f275c1fb1ca353dc8d391487 |
| 00B_PROJECT_RULES.md | 32096 | 1cfb654c4c41a83fc6e07370bbf2fcd4d70b1ffbc5b7c42d4b5b8874a59f7e1c |
| 00_PROJECT_OVERVIEW.md | 14437 | 8bc688847398d8da245732db6b579f05876f4de6582b0bd37cf128a26475f571 |
| 01_CORE_AUDIT.md | 45774 | 97946f9b4cde7c43f6fd82af09b8921d214df139304771b51324fd03692a177a |
| 02_DATA_AUDIT.md | 36222 | 427037500d2641d3d2c404d3b54ace0ea525c5d206c2103582d2754d9697b088 |
| 03A_INDICATORS_TREND.md | 11787 | 1180a5ccc174cb91857bb5796be15cbc258c71fbb7e8c4993f6e985a9cb0649a |
| 03B_INDICATORS_MOMENTUM.md | 5952 | 9a5a05b080b92ad4c1d9e8d3345292fd492f9fb01c21e56717d4b101e51bb589 |
| 03C_INDICATORS_VOLATILITY.md | 5660 | 461a54d0c52c578ef35bf86972cb673be6156cdf203f27310885a977c660ae33 |
| 03D_INDICATORS_STRUCTURE.md | 10672 | 349ca73f6f598f80fab10536668d89d59ab26455b20ad9d3564a6cdd228e9d16 |
| 03E_INDICATORS_PRICE_ACTION.md | 7814 | bba2ebbec374672d76018384f93de57cd12faf3a69d809fd631193a434724424 |
| 03F_INDICATORS_SESSIONS_VOLUME.md | 11362 | e4ee957f5bf234072528292ebb5e781c49d073da4b5699e8604d51dfb1980206 |
| 03G_INDICATORS_DIAGNOSTICS.md | 7822 | d8c6bd1b3e43bed51fd1cc750f5c54a74e70c9898dd8d40f6cfd4f4ef3c86c0c |
| 03_INDICATORS_AUDIT.md | 22678 | 91c11410cb4d63bc1839bb4ea17b17a226f7ab19bd99ed30e3ded2a855151d41 |
| 04_STRATEGIES_AUDIT.md | 5500 | 9c790d8df9351047d75edff3f881ff2ba067dd7cc8b829eb92f2af17d9ec49fd |
| 05A_TESTS_MODELS_COSTS_PORTFOLIO.md | 9213 | c16b6a8ae748829253464b50240adce4a6452073c4d92cfc2a385e6ccc423f32 |
| 05B_TESTS_ENGINE_REVIEW.md | 17394 | 22528df8febfa7fce9f08b92d2a50b0505ed3d04beeca6ba58874a763c2b9163 |
| 05C_TESTS_DATA.md | 17188 | e42ffcce71dfaa7c5bc0d7edbbf6b041593f401c1cde09d44ee365a7800fd8db |
| 05D_TESTS_INDICATORS.md | 21127 | bb537dce810792d5fddc461d4410b3c987c69c973a26feb0d31f53875bbee3df |
| 05E_TESTS_ENVIRONMENT.md | 1266 | da8ea17a7033020b114bf6350dae8115ce1095b43b4e5be75d9d5771e37c25a1 |
| 05_TESTS_AUDIT.md | 4891 | 1d59fda15300c7b612ed5daad57bcb56bf9d536ea09e970920863e697e52addf |
| 06_VALIDATION_AUDIT.md | 3855 | 92ffeb074c972434df66f2905408a0a5463fafc8365f9a4fe6b9fb8688154cb5 |
| 07_TEST_RESULTS.md | 68427 | c090e4b30ff9f55f901b507eb49a606487e23699e7434a5f112a2f056a7b5a95 |
| 08_AUDIT_HANDOFF.md | 6952 | d52bdb6f274b1f602932da62dd8e2ffff1bff588e9c0980db98c0a4bc7d4975c |


## File ngoài phạm vi

Không có source thuộc danh mục chưa đóng gói. Lịch sử giá, cache, bí mật, môi trường, Git và báo cáo cũ bị loại theo chỉ thị; xem 08_AUDIT_HANDOFF.md.

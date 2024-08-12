##########################################################
#            BASIC CLASSIFICATION FUNCTIONS              #
##########################################################
# rcATT is a tool to prediction tactics and techniques 
# from the ATT&CK framework, using multilabel text
# classification and post processing.
# Version:    1.00
# Author:     Valentine Legoy
# Date:       2019_10_22
# Important global constants and functions for
# classifications: training and prediction.

import joblib
import pandas as pd

from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import chi2, SelectPercentile

from nltk.corpus import stopwords

import classification_tools.preprocessing as prp
import classification_tools.postprocessing as pop

##########################################################
#       LABELS AND DATAFRAME LISTS AND RELATIONSHIP      #
##########################################################

TEXT_FEATURES = ["processed"]
CODE_TACTICS = ["TA0006","TA0002","TA0040","TA0003","TA0004","TA0008","TA0005","TA0010","TA0007","TA0009","TA0011","TA0001"]
NAME_TACTICS = ["Credential Access","Execution","Impact","Persistence","Privilege Escalation","Lateral Movement","Defense Evasion","Exfiltration","Discovery","Collection","Command and Control","Initial Access"]
CODE_TECHNIQUES = ["T1066","T1047","T1156","T1113","T1067","T1037","T1033","T1003","T1129","T1492","T1044","T1171","T1014","T1501","T1123","T1133","T1109","T1099","T1069","T1114","T1163","T1025","T1116","T1093","T1178","T1013","T1192","T1489","T1206","T1063","T1080","T1167","T1165","T1137","T1089","T1487","T1214","T1119","T1115","T1103","T1007","T1040","T1135","T1120","T1082","T1071","T1053","T1162","T1176","T1106","T1058","T1202","T1024","T1091","T1005","T1140","T1195","T1190","T1219","T1079","T1036","T1055","T1205","T1218","T1038","T1050","T1010","T1032","T1062","T1182","T1029","T1004","T1009","T1076","T1131","T1181","T1483","T1185","T1021","T1207","T1107","T1145","T1112","T1491","T1155","T1217","T1183","T1085","T1031","T1092","T1222","T1179","T1019","T1042","T1117","T1054","T1108","T1193","T1215","T1101","T1177","T1125","T1144","T1045","T1016","T1198","T1087","T1090","T1059","T1482","T1175","T1020","T1070","T1083","T1138","T1191","T1188","T1074","T1049","T1064","T1051","T1497","T1102","T1104","T1480","T1204","T1196","T1057","T1141","T1041","T1060","T1023","T1026","T1122","T1015","T1212","T1210","T1142","T1199","T1098","T1170","T1048","T1097","T1110","T1001","T1039","T1078","T1073","T1068","T1208","T1027","T1201","T1187","T1486","T1488","T1174","T1002","T1081","T1128","T1056","T1203","T1168","T1100","T1186","T1184","T1095","T1075","T1012","T1030","T1028","T1034","T1499","T1065","T1197","T1088","T1493","T1132","T1500","T1223","T1213","T1194","T1200","T1485","T1130","T1022","T1189","T1498","T1158","T1221","T1134","T1209","T1111","T1159","T1136","T1018","T1046","T1052","T1105","T1084","T1160","T1484","T1220","T1173","T1008","T1096","T1124","T1035","T1086","T1490","T1216","T1094","T1043","T1211","T1127","T1077"]
NAME_TECHNIQUES = ["Indicator Removal from Tools","Windows Management Instrumentation",".bash_profile and .bashrc","Screen Capture","Bootkit","Logon Scripts","System Owner/User Discovery","Credential Dumping","Execution through Module Load","Stored Data Manipulation","File System Permissions Weakness","LLMNR/NBT-NS Poisoning and Relay","Rootkit","Systemd Service","Audio Capture","External Remote Services","Component Firmware","Timestomp","Permission Groups Discovery","Email Collection","Rc.common","Data from Removable Media","Code Signing","Process Hollowing","SID-History Injection","Port Monitors","Spearphishing Link","Service Stop","Sudo Caching","Security Software Discovery","Taint Shared Content","Securityd Memory","Startup Items","Office Application Startup","Disabling Security Tools","Disk Structure Wipe","Credentials in Registry","Automated Collection","Clipboard Data","AppInit DLLs","System Service Discovery","Network Sniffing","Network Share Discovery","Peripheral Device Discovery","System Information Discovery","Standard Application Layer Protocol","Scheduled Task","Login Item","Browser Extensions","Execution through API","Service Registry Permissions Weakness","Indirect Command Execution","Custom Cryptographic Protocol","Replication Through Removable Media","Data from Local System","Deobfuscate/Decode Files or Information","Supply Chain Compromise","Exploit Public-Facing Application","Remote Access Tools","Multilayer Encryption","Masquerading","Process Injection","Port Knocking","Signed Binary Proxy Execution","DLL Search Order Hijacking","New Service","Application Window Discovery","Standard Cryptographic Protocol","Hypervisor","AppCert DLLs","Scheduled Transfer","Winlogon Helper DLL","Binary Padding","Remote Desktop Protocol","Authentication Package","Extra Window Memory Injection","Domain Generation Algorithms","Man in the Browser","Remote Services","DCShadow","File Deletion","Private Keys","Modify Registry","Defacement","AppleScript","Browser Bookmark Discovery","Image File Execution Options Injection","Rundll32","Modify Existing Service","Communication Through Removable Media","File Permissions Modification","Hooking","System Firmware","Change Default File Association","Regsvr32","Indicator Blocking","Redundant Access","Spearphishing Attachment","Kernel Modules and Extensions","Security Support Provider","LSASS Driver","Video Capture","Gatekeeper Bypass","Software Packing","System Network Configuration Discovery","SIP and Trust Provider Hijacking","Account Discovery","Connection Proxy","Command-Line Interface","Domain Trust Discovery","Distributed Component Object Model","Automated Exfiltration","Indicator Removal on Host","File and Directory Discovery","Application Shimming","CMSTP","Multi-hop Proxy","Data Staged","System Network Connections Discovery","Scripting","Shared Webroot","Virtualization/Sandbox Evasion","Web Service","Multi-Stage Channels","Execution Guardrails","User Execution","Control Panel Items","Process Discovery","Input Prompt","Exfiltration Over Command and Control Channel","Registry Run Keys / Startup Folder","Shortcut Modification","Multiband Communication","Component Object Model Hijacking","Accessibility Features","Exploitation for Credential Access","Exploitation of Remote Services","Keychain","Trusted Relationship","Account Manipulation","Mshta","Exfiltration Over Alternative Protocol","Pass the Ticket","Brute Force","Data Obfuscation","Data from Network Shared Drive","Valid Accounts","DLL Side-Loading","Exploitation for Privilege Escalation","Kerberoasting","Obfuscated Files or Information","Password Policy Discovery","Forced Authentication","Data Encrypted for Impact","Disk Content Wipe","Password Filter DLL","Data Compressed","Credentials in Files","Netsh Helper DLL","Input Capture","Exploitation for Client Execution","Local Job Scheduling","Web Shell","Process Doppelgänging","SSH Hijacking","Standard Non-Application Layer Protocol","Pass the Hash","Query Registry","Data Transfer Size Limits","Windows Remote Management","Path Interception","Endpoint Denial of Service","Uncommonly Used Port","BITS Jobs","Bypass User Account Control","Transmitted Data Manipulation","Data Encoding","Compile After Delivery","Compiled HTML File","Data from Information Repositories","Spearphishing via Service","Hardware Additions","Data Destruction","Install Root Certificate","Data Encrypted","Drive-by Compromise","Network Denial of Service","Hidden Files and Directories","Template Injection","Access Token Manipulation","Time Providers","Two-Factor Authentication Interception","Launch Agent","Create Account","Remote System Discovery","Network Service Scanning","Exfiltration Over Physical Medium","Remote File Copy","Windows Management Instrumentation Event Subscription","Launch Daemon","Group Policy Modification","XSL Script Processing","Dynamic Data Exchange","Fallback Channels","NTFS File Attributes","System Time Discovery","Service Execution","PowerShell","Inhibit System Recovery","Signed Script Proxy Execution","Custom Command and Control Protocol","Commonly Used Port","Exploitation for Defense Evasion","Trusted Developer Utilities","Windows Admin Shares"]
ALL_TTPS = ["TA0006","TA0002","TA0040","TA0003","TA0004","TA0008","TA0005","TA0010","TA0007","TA0009","TA0011","TA0001","T1066","T1047","T1156","T1113","T1067","T1037","T1033","T1003","T1129","T1492","T1044","T1171","T1014","T1501","T1123","T1133","T1109","T1099","T1069","T1114","T1163","T1025","T1116","T1093","T1178","T1013","T1192","T1489","T1206","T1063","T1080","T1167","T1165","T1137","T1089","T1487","T1214","T1119","T1115","T1103","T1007","T1040","T1135","T1120","T1082","T1071","T1053","T1162","T1176","T1106","T1058","T1202","T1024","T1091","T1005","T1140","T1195","T1190","T1219","T1079","T1036","T1055","T1205","T1218","T1038","T1050","T1010","T1032","T1062","T1182","T1029","T1004","T1009","T1076","T1131","T1181","T1483","T1185","T1021","T1207","T1107","T1145","T1112","T1491","T1155","T1217","T1183","T1085","T1031","T1092","T1222","T1179","T1019","T1042","T1117","T1054","T1108","T1193","T1215","T1101","T1177","T1125","T1144","T1045","T1016","T1198","T1087","T1090","T1059","T1482","T1175","T1020","T1070","T1083","T1138","T1191","T1188","T1074","T1049","T1064","T1051","T1497","T1102","T1104","T1480","T1204","T1196","T1057","T1141","T1041","T1060","T1023","T1026","T1122","T1015","T1212","T1210","T1142","T1199","T1098","T1170","T1048","T1097","T1110","T1001","T1039","T1078","T1073","T1068","T1208","T1027","T1201","T1187","T1486","T1488","T1174","T1002","T1081","T1128","T1056","T1203","T1168","T1100","T1186","T1184","T1095","T1075","T1012","T1030","T1028","T1034","T1499","T1065","T1197","T1088","T1493","T1132","T1500","T1223","T1213","T1194","T1200","T1485","T1130","T1022","T1189","T1498","T1158","T1221","T1134","T1209","T1111","T1159","T1136","T1018","T1046","T1052","T1105","T1084","T1160","T1484","T1220","T1173","T1008","T1096","T1124","T1035","T1086","T1490","T1216","T1094","T1043","T1211","T1127","T1077"]
STIX_IDENTIFIERS = ["x-mitre-tactic--2558fd61-8c75-4730-94c4-11926db2a263","x-mitre-tactic--4ca45d45-df4d-4613-8980-bac22d278fa5","x-mitre-tactic--5569339b-94c2-49ee-afb3-2222936582c8","x-mitre-tactic--5bc1d813-693e-4823-9961-abf9af4b0e92","x-mitre-tactic--5e29b093-294e-49e9-a803-dab3d73b77dd","x-mitre-tactic--7141578b-e50b-4dcc-bfa4-08a8dd689e9e","x-mitre-tactic--78b23412-0651-46d7-a540-170a1ce8bd5a","x-mitre-tactic--9a4e74ab-5008-408c-84bf-a10dfbc53462","x-mitre-tactic--c17c5845-175e-4421-9713-829d0573dbc9","x-mitre-tactic--d108ce10-2419-4cf9-a774-46161d6c6cfe","x-mitre-tactic--f72804c5-f15a-449e-a5da-2eecd181f813","x-mitre-tactic--ffd5bcee-6e16-4dd2-8eca-7b3beedf33ca","attack-pattern--00d0b012-8a03-410e-95de-5826bf542de6","attack-pattern--01a5a209-b94c-450b-b7f9-946497d91055","attack-pattern--01df3350-ce05-4bdf-bdf8-0a919a66d4a8","attack-pattern--0259baeb-9f63-4c69-bf10-eb038c390688","attack-pattern--02fefddc-fb1b-423f-a76b-7552dd211d4d","attack-pattern--03259939-0b57-482f-8eb5-87c0e0d54334","attack-pattern--03d7999c-1f4c-42cc-8373-e7690d318104","attack-pattern--0a3ead4e-6d47-4ccb-854c-a6a4f9d96b22","attack-pattern--0a5231ec-41af-4a35-83d0-6bdf11f28c65","attack-pattern--0bf78622-e8d2-41da-a857-731472d61a92","attack-pattern--0ca7beef-9bbc-4e35-97cf-437384ddce6a","attack-pattern--0dbf5f1b-a560-4d51-ac1b-d70caab3e1f0","attack-pattern--0f20e3cb-245b-4a61-8a91-2d93f7cb0e9b","attack-pattern--0fff2797-19cb-41ea-a5f1-8a9303b8158e","attack-pattern--1035cdf2-3e5f-446f-a7a7-e8f6d7925967","attack-pattern--10d51417-ee35-4589-b1ff-b6df1c334e8d","attack-pattern--10d5f3b7-6be6-4da5-9a77-0f1e2bbfcc44","attack-pattern--128c55d3-aeba-469f-bd3e-c8996ab4112a","attack-pattern--15dbf668-795c-41e6-8219-f0447c0e64ce","attack-pattern--1608f3e1-598a-42f4-a01a-2e252e81728f","attack-pattern--18d4ab39-12ed-4a16-9fdb-ae311bba4a0f","attack-pattern--1b7ba276-eedc-4951-a762-0ceea2c030ec","attack-pattern--1b84d551-6de8-4b96-9930-d177677c3b1d","attack-pattern--1c338d0f-a65e-4073-a5c1-c06878849f21","attack-pattern--1df0326d-2fbc-4d08-a16b-48365f1e742d","attack-pattern--1f47e2fd-fa77-4f2f-88ee-e85df308f125","attack-pattern--20138b9d-1aac-4a26-8654-a36b6bbf2bba","attack-pattern--20fb2507-d71c-455d-9b6d-6104461cf26b","attack-pattern--2169ba87-1146-4fc7-a118-12b72251db7e","attack-pattern--241814ae-de3f-4656-b49e-f9a80764d4b7","attack-pattern--246fd3c7-f5e3-466d-8787-4c13d9e3b61c","attack-pattern--2715c335-1bf2-4efe-9f18-0691317ff83b","attack-pattern--2ba5aa71-9d15-4b22-b726-56af06d9ad2f","attack-pattern--2c4d4e92-0ccf-4a97-b54c-86d662988a53","attack-pattern--2e0dd10b-676d-4964-acd0-8a404c92b044","attack-pattern--2e114e45-2c50-404c-804a-3af9564d240e","attack-pattern--2edd9d6a-5674-4326-a600-ba56de467286","attack-pattern--30208d3e-0d6b-43c8-883e-44462a514619","attack-pattern--30973a08-aed9-4edf-8604-9084ce1b5c4f","attack-pattern--317fefa6-46c7-4062-adb6-2008cf6bcb41","attack-pattern--322bad5a-1c49-4d23-ab79-76d641794afa","attack-pattern--3257eb21-f9a7-4430-8de1-d8b6e288f529","attack-pattern--3489cfc5-640f-4bb3-a103-9137b97de79f","attack-pattern--348f1eef-964b-4eb6-bb53-69b3dcb0c643","attack-pattern--354a7f88-63fb-41b5-a801-ce3b377b36f1","attack-pattern--355be19c-ffc9-46d5-8d50-d6a036c675b6","attack-pattern--35dd844a-b219-4e2b-a6bb-efa9a75995a9","attack-pattern--36675cd3-fe00-454c-8516-aebecacbe9d9","attack-pattern--389735f1-f21c-4208-b8f0-f8031e7169b8","attack-pattern--391d824f-0ef1-47a0-b0ee-c59a75e27670","attack-pattern--39a130e1-6ab7-434a-8bd2-418e7d9d6427","attack-pattern--3b0e52ce-517a-4614-a523-1bd5deef6c5e","attack-pattern--3b3cbbe0-6ed3-4334-b543-3ddfd8c5642d","attack-pattern--3b744087-9945-4a6f-91e8-9dbceda417a4","attack-pattern--3c4a2599-71ee-4405-ba1e-0e28414b4bc5","attack-pattern--3ccef7ae-cb5e-48f6-8302-897105fbf55c","attack-pattern--3f18edba-28f4-4bb9-82c3-8aa60dcac5f7","attack-pattern--3f886f2a-874f-4333-b794-aa6075009b1c","attack-pattern--4061e78c-1284-44b4-9116-73e4ac3912f7","attack-pattern--428ca9f8-0e33-442a-be87-f869cb4cf73e","attack-pattern--42e8de7b-37b2-4258-905a-6897815e58e0","attack-pattern--43e7dc91-05b2-474c-b9ac-2ed4fe101f4d","attack-pattern--451a9977-d255-43c9-b431-66de80130c8c","attack-pattern--457c7820-d331-465a-915e-42f85500ccc4","attack-pattern--46944654-fcc1-4f63-9dad-628102376586","attack-pattern--478aa214-2ca7-4ec0-9978-18798e514790","attack-pattern--4ae4f953-fe58-4cc8-a327-33257e30a830","attack-pattern--4b74a1d4-b0e9-4ef1-93f1-14ecc6e2f5b5","attack-pattern--4be89c7c-ace6-4876-9377-c8d54cef3d63","attack-pattern--4bf5845d-a814-4490-bc5c-ccdee6043025","attack-pattern--4eeaf8a9-c86b-4954-a663-9555fb406466","attack-pattern--514ede4c-78b3-4d78-a38b-daddf6217a79","attack-pattern--519630c5-f03f-4882-825c-3af924935817","attack-pattern--51dea151-0898-4a45-967c-3ebee0420484","attack-pattern--52d40641-c480-4ad5-81a3-c80ccaddf82d","attack-pattern--52f3d5a6-8a0f-4f82-977e-750abf90d0b0","attack-pattern--54456690-84de-4538-9101-643e26437e09","attack-pattern--544b0346-29ad-41e1-a808-501bb4193f47","attack-pattern--54a649ff-439a-41a4-9856-8d144a2551ba","attack-pattern--564998d8-ab3e-4123-93fb-eccaa6b9714a","attack-pattern--56fca983-1cf1-4fd1-bda0-5e170a37ab59","attack-pattern--56ff457d-5e39-492b-974c-dfd2b8603ffe","attack-pattern--57340c81-c025-4189-8fa0-fc7ede51bae4","attack-pattern--5909f20f-3c39-4795-be06-ef1ea40d350b","attack-pattern--5ad95aaa-49c1-4784-821d-2e83f47b079b","attack-pattern--5e4a2073-9643-44cb-a0b5-e7f4048446c7","attack-pattern--62166220-e498-410f-a90a-19d4339d4e99","attack-pattern--62b8c999-dcc0-4755-bd69-09442d9359f5","attack-pattern--62dfd1ca-52d5-483c-a84b-d6e80bf94b7b","attack-pattern--64196062-5210-42c3-9a02-563a0d1797ef","attack-pattern--65917ae0-b854-4139-83fe-bf2441cf0196","attack-pattern--66f73398-8394-4711-85e5-34c8540b22a5","attack-pattern--6856ddd6-2df3-4379-8b87-284603c189c3","attack-pattern--68c96494-1a50-403e-8844-69a6af278c68","attack-pattern--68f7e3a1-f09f-4164-9a62-16b648a0dd5a","attack-pattern--6a5848a8-6201-4a2c-8a6a-ca5af8c6f3df","attack-pattern--6aabc5ec-eae6-422c-8311-38d45ee9838a","attack-pattern--6aac77c4-eaf2-4366-8c13-ce50ab951f38","attack-pattern--6be14413-578e-46c1-8304-310762b3ecd5","attack-pattern--6c174520-beea-43d9-aac6-28fb77f3e446","attack-pattern--6e6845c2-347a-4a6f-a2d1-b74a18ebd352","attack-pattern--6faf650d-bf31-4eb4-802d-1000cf38efaf","attack-pattern--6fb6408c-0db3-41d9-a3a1-a32e5f16454e","attack-pattern--6ff403bc-93e3-48be-8687-e102fdba8c88","attack-pattern--707399d6-ab3e-4963-9315-d9d3818cd6a0","attack-pattern--72b5ef57-325c-411b-93ca-a3ca6fa17e31","attack-pattern--72b74d71-8169-42aa-92e0-e7b04b9f5a08","attack-pattern--731f4f55-b6d0-41d1-a7a9-072a66389aea","attack-pattern--7385dfaf-6886-4229-9ecd-6fd678040830","attack-pattern--767dbf9e-df3f-45cb-8998-4903ab5f80c0","attack-pattern--772bc7a8-a157-42cc-8728-d648e25c7fe7","attack-pattern--774a3188-6ba9-4dc4-879d-d54ee48a5ce9","attack-pattern--799ace7f-e227-4411-baa0-8868704f2a69","attack-pattern--7bc57495-ea59-4380-be31-a64af124ef18","attack-pattern--7c93aa74-4bc0-4a9e-90ea-f25f86301566","attack-pattern--7d6f590f-544b-45b4-9a42-e0805f342af3","attack-pattern--7d751199-05fa-4a72-920f-85df4506c76c","attack-pattern--7dd95ff6-712e-4056-9626-312ea4ab4c5e","attack-pattern--7e150503-88e7-4861-866b-ff1ac82c4475","attack-pattern--7fd87010-3a00-4da3-b905-410525e8ec44","attack-pattern--804c042c-cfe6-449e-bc1a-ba0a998a70db","attack-pattern--82caa33e-d11a-433a-94ea-9b5a5fbef81d","attack-pattern--830c9528-df21-472c-8c14-a036bf17d665","attack-pattern--84e02621-8fdf-470f-bd58-993bb6a89d91","attack-pattern--853c4192-4311-43e1-bfbb-b11b14911852","attack-pattern--8c32eb4d-805f-4fc5-bf60-c4d476c131b5","attack-pattern--8df54627-376c-487c-a09c-7d2b5620f56e","attack-pattern--8f4a33ec-8b1f-4b80-a2f6-642b2e479580","attack-pattern--91ce1ede-107f-4d8b-bf4c-735e8789c94b","attack-pattern--92d7da27-2d91-488e-a00c-059dc162766d","attack-pattern--9422fc14-1c43-410d-ab0f-a709b76c72dc","attack-pattern--970cdb5c-02fb-4c38-b17e-d6327cf3c810","attack-pattern--99709758-2b96-48f2-a68a-ad7fbd828091","attack-pattern--9b52fca7-1a36-4da0-b62d-da5bd83b4d69","attack-pattern--9b99b83a-1aac-4e29-b975-b374950551a3","attack-pattern--9c306d8d-cde7-4b4c-b6e8-d0bb16caca36","attack-pattern--9db0cf3a-a3c9-4012-8268-123b9db6fd82","attack-pattern--9e09ddb2-1746-4448-9cad-7f8b41777d6d","attack-pattern--9fa07bef-9c81-421e-a8e5-ad4366c5a925","attack-pattern--a10641f4-87b4-45a3-a906-92a149cb2c27","attack-pattern--a127c32c-cbb0-4f9d-be07-881a792408ec","attack-pattern--a19e86f8-1c0a-4fea-8407-23b73d615776","attack-pattern--a257ed11-ff3b-4216-8c9d-3938ef57064c","attack-pattern--a93494bb-4b80-4ea1-8695-3236a49916fd","attack-pattern--ad255bfe-a9e6-4b52-a258-8d3462abe842","attack-pattern--ae676644-d2d2-41b7-af7e-9bed1b55898c","attack-pattern--b17a1a56-e99c-403c-8948-561df0cffe81","attack-pattern--b2001907-166b-4d71-bb3c-9d26c871de09","attack-pattern--b21c3b2d-02e6-45b1-980b-e69051040839","attack-pattern--b39d03cb-7b98-41c4-a878-c40c1a913dc0","attack-pattern--b3d682b6-98f2-4fb0-aa3b-b4df007ca70a","attack-pattern--b6075259-dba3-44e9-87c7-e954f37ec0d5","attack-pattern--b77cf5f3-6060-475d-bd60-40ccbf28fdc2","attack-pattern--b80d107d-fa0d-4b60-9684-b0433e8bdba0","attack-pattern--b82f7d37-b826-4ec9-9391-8e121c78aed7","attack-pattern--b8c5c9dd-a662-479d-9428-ae745872537c","attack-pattern--b9f5dbe2-4c55-4fc5-af2e-d42c1d182ec4","attack-pattern--ba8e391f-14b5-496f-81f2-2d5ecd646c1c","attack-pattern--bb0e0cb5-f3e4-4118-a4cb-6bf13bfbc9f2","attack-pattern--bb5a00de-e086-4859-a231-fa793f6797e2","attack-pattern--be2dcee9-a7a7-4e38-afd6-21b31ecc3d63","attack-pattern--c0a384a4-9a25-40e1-97b6-458388474bc8","attack-pattern--c16e5409-ee53-4d79-afdc-4099dc9292df","attack-pattern--c1a452f3-6499-4c12-b7e9-a6a0a102af76","attack-pattern--c1b11bf7-c68e-4fbf-a95b-28efbe7953bb","attack-pattern--c21d5a77-d422-4a69-acd7-2c53c1faa34b","attack-pattern--c23b740b-a42b-47a1-aec2-9d48ddd547ff","attack-pattern--c32f7008-9fea-41f7-8366-5eb9b74bd896","attack-pattern--c3888c54-775d-4b2f-b759-75a2ececcbfd","attack-pattern--c3bce4f4-9795-46c6-976e-8676300bbc39","attack-pattern--c4ad009b-6e13-4419-8d21-918a1652de02","attack-pattern--c675646d-e204-4aa8-978d-e3d6d65885c4","attack-pattern--c848fcf7-6b62-4bde-8216-b6c157d48da0","attack-pattern--c8e87b83-edbb-48d4-9295-4974897525b7","attack-pattern--ca1a3f50-5ebd-41f8-8320-2c7d6a6e88be","attack-pattern--cc1e737c-236c-4e3b-83ba-32039a626ef8","attack-pattern--cc7b8c4e-9be0-47ca-b0bb-83915ec3ee2f","attack-pattern--cf7b3a06-8b42-4c33-bbe9-012120027925","attack-pattern--d21a2069-23d5-4043-ad6d-64f6b644cb1a","attack-pattern--d28ef391-8ed4-45dc-bc4a-2f43abf54416","attack-pattern--d3df754e-997b-4cf9-97d4-70feb3120847","attack-pattern--d40239b3-05ff-46d8-9bdd-b46d13463ef9","attack-pattern--d45a3d09-b3cf-48f4-9f0f-f521ee5cb05c","attack-pattern--d519cfd5-f3a8-43a9-a846-ed0bb40672b1","attack-pattern--d54416bd-0803-41ca-870a-ce1af7c05638","attack-pattern--d742a578-d70e-4d0e-96a6-02a9c30204e6","attack-pattern--d74c4a7e-ffbf-432f-9365-7ebf1f787cab","attack-pattern--dc27c2ec-c5f9-4228-ba57-d67b590bda93","attack-pattern--dc31fe1e-d722-49da-8f5f-92c7b5aff534","attack-pattern--dcaa092b-7de9-4a21-977f-7fcb77e89c48","attack-pattern--dce31a00-1e90-4655-b0f9-e2e71a748a87","attack-pattern--dd43c543-bb85-4a6f-aa6e-160d90d06a49","attack-pattern--dd901512-6e37-4155-943b-453e3777b125","attack-pattern--e01be9c5-e763-4caf-aeb7-000b416aef67","attack-pattern--e358d692-23c0-4a31-9eb6-ecc13a8d7735","attack-pattern--e3a12395-188d-4051-9a16-ea8e14d07b88","attack-pattern--e6415f09-df0e-48de-9aba-928c902b7549","attack-pattern--e6919abc-99f9-4c6c-95a5-14761e7b2add","attack-pattern--e906ae4d-1d3a-4675-be23-22f7311c0da4","attack-pattern--e99ec083-abdd-48de-ad87-4dbf6f8ba2a4","attack-pattern--ebb42bbe-62d7-47d7-a55f-3b08b61d792d","attack-pattern--ebbe170d-aa74-4946-8511-9921243415a3","attack-pattern--edbe24e9-aec4-4994-ac75-6a6bc7f1ddd0","attack-pattern--f24faf46-3b26-4dbb-98f2-63460498e433","attack-pattern--f2d44246-91f1-478a-b6c8-1227e0ca109d","attack-pattern--f3c544dc-673c-4ef3-accb-53229f1ae077","attack-pattern--f44731de-ea9f-406d-9b83-30ecbb9b4392","attack-pattern--f4882e23-8aa7-4b12-b28a-b349c12ee9e0","attack-pattern--f5d8eed6-48a9-4cdf-a3d7-d1ffa99c3d2a","attack-pattern--f6fe9070-7a65-49ea-ae72-76292f42cebe","attack-pattern--f72eb8a8-cd4c-461d-a814-3f862befbf00","attack-pattern--f879d51c-5476-431c-aedf-f14d207e4d1e","attack-pattern--fe926152-f431-4baf-956c-4ad3cb0bf23b","attack-pattern--ff25900d-76d5-449b-a351-8824e62fc81b","attack-pattern--ffe742ed-9100-4686-9e00-c331da544787"]

TACTICS_TECHNIQUES_RELATIONSHIP_DF = pd.DataFrame({"TA0001":pd.Series(["T1133","T1192","T1091","T1195","T1190","T1193","T1199","T1078","T1194","T1200","T1189"]),
										"TA0002":pd.Series(["T1047","T1129","T1121","T1053","T1106","T1218","T1153","T1152","T1155","T1085","T1117","T1177","T1059","T1191","T1064","T1204","T1196","T1072","T1170","T1061","T1154","T1203","T1168","T1028","T1223","T1151","T1220","T1173","T1035","T1086","T1216","T1118","T1127"]),
										"TA0003":pd.Series(["T1156","T1067","T1037","T1161","T1150","T1044","T1501","T1133","T1109","T1163","T1013","T1180","T1165","T1137","T1103","T1053","T1162","T1176","T1058","T1205","T1038","T1050","T1062","T1182","T1004","T1131","T1152","T1183","T1031","T1179","T1019","T1042","T1164","T1108","T1215","T1101","T1177","T1198","T1138","T1060","T1023","T1122","T1015","T1098","T1157","T1078","T1154","T1128","T1168","T1166","T1100","T1034","T1197","T1158","T1209","T1159","T1136","T1084","T1160"]),
										"TA0004":pd.Series(["T1150","T1044","T1178","T1013","T1206","T1165","T1103","T1053","T1058","T1055","T1038","T1050","T1182","T1181","T1183","T1179","T1138","T1015","T1169","T1157","T1078","T1068","T1166","T1100","T1034","T1088","T1134","T1160"]),
										"TA0005":pd.Series(["T1066","T1143","T1150","T1148","T1006","T1014","T1109","T1099","T1116","T1093","T1121","T1089","T1202","T1140","T1036","T1055","T1205","T1218","T1038","T1009","T1181","T1152","T1207","T1107","T1112","T1183","T1085","T1222","T1117","T1054","T1108","T1144","T1045","T1198","T1070","T1191","T1064","T1497","T1102","T1480","T1196","T1122","T1149","T1170","T1078","T1073","T1027","T1186","T1197","T1088","T1147","T1500","T1223","T1146","T1130","T1158","T1221","T1134","T1151","T1126","T1484","T1220","T1096","T1216","T1118","T1211","T1127"]),
										"TA0006":pd.Series(["T1003","T1171","T1167","T1214","T1040","T1139","T1145","T1179","T1141","T1212","T1142","T1098","T1110","T1208","T1187","T1174","T1081","T1056","T1111"]),
										"TA0007":pd.Series(["T1033","T1069","T1063","T1007","T1040","T1135","T1120","T1082","T1010","T1217","T1016","T1087","T1482","T1083","T1049","T1497","T1057","T1201","T1012","T1018","T1046","T1124"]),
										"TA0008":pd.Series(["T1037","T1080","T1017","T1091","T1076","T1021","T1155","T1175","T1051","T1072","T1210","T1097","T1184","T1075","T1028","T1105","T1077"]),
										"TA0009":pd.Series(["T1113","T1123","T1114","T1025","T1119","T1115","T1005","T1185","T1125","T1074","T1039","T1056","T1213"]),
										"TA0010":pd.Series(["T1029","T1011","T1020","T1041","T1048","T1002","T1030","T1022","T1052"]),
										"TA0011":pd.Series(["T1172","T1071","T1024","T1219","T1079","T1205","T1032","T1483","T1092","T1090","T1188","T1102","T1104","T1026","T1001","T1095","T1065","T1132","T1105","T1008","T1094","T1043"]),
										"TA0040":pd.Series(["T1492","T1489","T1487","T1491","T1486","T1488","T1499","T1494","T1493","T1496","T1485","T1498","T1495","T1490"])
                                        })
										
##########################################################
#             RETRAIN AND PREDICT FUNCTIONS              #
##########################################################

def train(cmd):
	"""
	Train again rcATT with a new dataset
	"""
	
	# stopwords with additional words found during the development
	stop_words = stopwords.words('english')
	new_stop_words = ["'ll", "'re", "'ve", 'ha', 'wa',"'d", "'s", 'abov', 'ani', 'becaus', 'befor', 'could', 'doe', 'dure', 'might', 'must', "n't", 'need', 'onc', 'onli', 'ourselv', 'sha', 'themselv', 'veri', 'whi', 'wo', 'would', 'yourselv']
	stop_words.extend(new_stop_words)
	
	# load all possible data
	train_data_df = pd.read_csv('classification_tools/data/training_data_original.csv', encoding = "ISO-8859-1")
	train_data_added = pd.read_csv('classification_tools/data/training_data_added.csv', encoding = "ISO-8859-1")
	train_data_df = pd.concat([train_data_df, train_data_added], ignore_index=True)

	train_data_df = prp.processing(train_data_df)

	reports = train_data_df[TEXT_FEATURES]
	tactics = train_data_df[CODE_TACTICS]
	techniques = train_data_df[CODE_TECHNIQUES]
	
	if cmd:
		pop.print_progress_bar(0)
	
	# Define a pipeline combining a text feature extractor with multi label classifier for tactics prediction
	pipeline_tactics = Pipeline([
			('columnselector', prp.TextSelector(key = 'processed')),
			('tfidf', TfidfVectorizer(tokenizer = prp.LemmaTokenizer(), stop_words = stop_words, max_df = 0.90)),
			('selection', SelectPercentile(chi2, percentile = 50)),
			('classifier', OneVsRestClassifier(LinearSVC(penalty = 'l2', loss = 'squared_hinge', dual = True, class_weight = 'balanced'), n_jobs = 1))
		])
	
	# train the model for tactics
	pipeline_tactics.fit(reports, tactics)
	
	if cmd:
		pop.print_progress_bar(2)
	
	# Define a pipeline combining a text feature extractor with multi label classifier for techniques prediction
	pipeline_techniques = Pipeline([
			('columnselector', prp.TextSelector(key = 'processed')),
			('tfidf', TfidfVectorizer(tokenizer = prp.StemTokenizer(), stop_words = stop_words, min_df = 2, max_df = 0.99)),
			('selection', SelectPercentile(chi2, percentile = 50)),
			('classifier', OneVsRestClassifier(LinearSVC(penalty = 'l2', loss = 'squared_hinge', dual = False, max_iter = 1000, class_weight = 'balanced'), n_jobs = 1))
		])
	
	# train the model for techniques
	pipeline_techniques.fit(reports, techniques)
	
	if cmd:
		pop.print_progress_bar(4)
	
	pop.find_best_post_processing(cmd)
	
	#Save model
	joblib.dump(pipeline_tactics, 'classification_tools/data/pipeline_tactics.joblib')
	joblib.dump(pipeline_techniques, 'classification_tools/data/pipeline_techniques.joblib')
	
def predict(report_to_predict, post_processing_parameters):
	"""
	Predict tactics and techniques from a report in a txt file.
	"""

	# loading the models
	pipeline_tactics = joblib.load('classification_tools/data/pipeline_tactics.joblib')
	pipeline_techniques = joblib.load('classification_tools/data/pipeline_techniques.joblib')

	report = prp.processing(pd.DataFrame([report_to_predict], columns = ['Text']))[TEXT_FEATURES]
	
	# predictions
	predprob_tactics = pipeline_tactics.decision_function(report)
	pred_tactics = pipeline_tactics.predict(report)

	predprob_techniques = pipeline_techniques.decision_function(report)
	pred_techniques = pipeline_techniques.predict(report)
	
	if post_processing_parameters[0] == "HN":
		# hanging node thresholds retrieval and hanging node performed on predictions if in parameters
		pred_techniques = pop.hanging_node(pred_tactics, predprob_tactics, pred_techniques, predprob_techniques, post_processing_parameters[1][0], post_processing_parameters[1][1])
	elif post_processing_parameters[0] == "CP":
		# confidence propagation performed on prediction if in parameters
		pred_techniques, predprob_techniques = pop.confidence_propagation(predprob_tactics, pred_techniques, predprob_techniques)
	
	return pred_tactics, predprob_tactics, pred_techniques, predprob_techniques
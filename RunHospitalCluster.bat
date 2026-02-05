@echo off
title MongoDB Hospital System Auto-Sharding (Healthcare_DB)
cls

:: [1] تحديد المسار الرئيسي للبيانات
set BASE_PATH=A:\Files\HealthCare\data\db

echo ====================================================
echo [1/4] Creating Dedicated Data Directories...
echo ====================================================
if not exist "%BASE_PATH%\cs1" mkdir "%BASE_PATH%\cs1"
if not exist "%BASE_PATH%\cs2" mkdir "%BASE_PATH%\cs2"
if not exist "%BASE_PATH%\cs3" mkdir "%BASE_PATH%\cs3"
if not exist "%BASE_PATH%\sh0" mkdir "%BASE_PATH%\sh0"
if not exist "%BASE_PATH%\sh1" mkdir "%BASE_PATH%\sh1"

echo.
echo [2/4] Starting 6 Servers (Config, Shards, Mongos)...
echo.

:: تشغيل خوادم الإعدادات
start "Config1" cmd /k "mongod --configsvr --replSet rshard --dbpath %BASE_PATH%\cs1 --port 2001"
start "Config2" cmd /k "mongod --configsvr --replSet rshard --dbpath %BASE_PATH%\cs2 --port 2002"
start "Config3" cmd /k "mongod --configsvr --replSet rshard --dbpath %BASE_PATH%\cs3 --port 2003"

:: تشغيل خوادم البيانات
start "Shard0" cmd /k "mongod --shardsvr --replSet shard0rep --dbpath %BASE_PATH%\sh0 --port 2005"
start "Shard1" cmd /k "mongod --shardsvr --replSet shard1rep --dbpath %BASE_PATH%\sh1 --port 2007"

:: تشغيل الموجه
timeout /t 10
start "MONGOS" cmd /k "mongos --port 2009 --configdb rshard/localhost:2001,localhost:2002,localhost:2003"

echo Waiting 25 seconds for all processes to start and stabilize...
timeout /t 25

echo.
echo [3/4] Running Internal Configuration...
echo.

:: 1. تهيئة الـ Config Servers
echo rs.initiate({_id:'rshard',configsvr:true,members:[{_id:0,host:'localhost:2001'},{_id:1,host:'localhost:2002'},{_id:2,host:'localhost:2003'}]}) | mongosh --port 2001
timeout /t 10

:: 2. تهيئة الـ Shards
echo rs.initiate({_id:'shard0rep',members:[{_id:0,host:'localhost:2005'}]}) | mongosh --port 2005
echo rs.initiate({_id:'shard1rep',members:[{_id:0,host:'localhost:2007'}]}) | mongosh --port 2007
timeout /t 15

:: 3. ربط الـ Shards وتفعيل التقسيم لـ 8 مجموعات
(
echo sh.addShard('shard0rep/localhost:2005');
echo sh.addShard('shard1rep/localhost:2007');
echo sh.enableSharding('healthcare_db');

:: المجموعات المقسمة (الآن تشمل الـ Users)
echo sh.shardCollection('healthcare_db.patients', {'_id': 'hashed'});
echo sh.shardCollection('healthcare_db.doctors', {'_id': 'hashed'});
echo sh.shardCollection('healthcare_db.users', {'email': 'hashed'});
echo sh.shardCollection('healthcare_db.appointments', {'_id': 'hashed'});
echo sh.shardCollection('healthcare_db.rooms', {'roomNumber': 'hashed'});
echo sh.shardCollection('healthcare_db.news', {'_id': 'hashed'});
echo sh.shardCollection('healthcare_db.operations', {'_id': 'hashed'});
echo sh.shardCollection('healthcare_db.applications', {'_id': 'hashed'});

echo print('====================================================');
echo print('SUCCESS: healthcare_db is fully configured!');
echo print('Sharded (8): patients, doctors, users, appointments, rooms, news, operations, applications');
echo print('Fixed on Primary (2): admins, departments');
echo print('====================================================');
) | mongosh --port 2009

echo.
echo [4/4] Finalizing...
pause
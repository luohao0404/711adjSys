# -*- coding: utf-8 -*-
from flask import Flask, jsonify, abort, make_response, request
#import peewee
import mysql.connector
#import sys
import json
from flask_cors import CORS,cross_origin
import datetime

#db = peewee.SqliteDatabase("data.db")

api = Flask(__name__)
CORS(api)

@api.route('/getAllUsers', methods=['GET'])
def getAllUsers():
    
    print "crossed"
    
    result = {}
    resultUser = []
    
    conn = mysql.connector.connect(user='root', password='root', host='localhost', database='seisan')
    cur = conn.cursor()
    
    # user 取得
    try:
        cur.execute("select * from user_mst;")
    except RuntimeError as e:
        print('MySQLdb.Error: ', e)
    
    
    # 例：[{"id":"1","name":"luo"},{"id":"2","name":"zhang"}]
    for row in cur.fetchall():
        resultUser.append({"id":row[0], "name":row[1]})
    

    result["user"] = resultUser
    
    cur.close
    conn.close
    
    print result
    
    resp = make_response(json.dumps(result, ensure_ascii=False))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    
    return resp


@api.route('/getDetailsByUsers', methods=['POST'])
def getDetailsByUsers():
    
    print "crossed"
    param = json.loads(request.data)
    userIdA = param["userA"]
    userIdB = param["userB"]
    
    result = {}
    resultAtoB = []
    resultBtoA = []
    
    conn = mysql.connector.connect(user='root', password='root', host='localhost', database='seisan')
    cur = conn.cursor()
    
    # 例：
    # var detailListAB = [{"userIdFrom":"1","userIdTo":"2","userNmFrom":"luo","userNmTo":"chen","payNum":"1","adNum":"10","use":"電気代","amount":"1000"}
    #                      ,{"userIdFrom":"2","userIdTo":"1","userNmFrom":"luo","userNmTo":"chen","payNum":"2","adNum":"20","use":"ガス代","amount":"2000"}];
        
    #var detailListBA = [{"userFrom":"chen","userTo":"luo","payNum":"3","adNum":"30","use":"12月スキー","amount":"3000"}
    #                     ,{"userFrom":"chen","userTo":"luo","payNum":"4","adNum":"40","use":"家賃","amount":"4000"}];
    sql = '''
        SELECT A.ad_detail_id as '0',
               A.pay_id as '1',
               A.ad_amount as '2',
               UA.name as '3',
               UB.name as '4',
               A.ad_date as '5',
               A.ad_done as '6',
               P.pay_content as '7',
               A.ad_from as '8',
               A.ad_to as '9'
               FROM seisan.adjustment_detail as A
               INNER JOIN seisan.pay_biz as P
               ON A.pay_id = P.pay_id
        LEFT JOIN seisan.user_mst as UA
        ON A.ad_from = UA.id
        LEFT JOIN seisan.user_mst as UB
        ON A.ad_to = UB.id
        WHERE A.ad_from = %s
            AND A.ad_to = %s
            AND A.ad_done <> 1
        ORDER BY 6 DESC, 2 DESC
        '''
    
    try:
        # sql発行
        cur.execute(sql, (userIdA ,userIdB))
    except RuntimeError as e:
        print('MySQLdb.Error: ', e)

    for row in cur.fetchall():
        resultAtoB.append({"userIdFrom":row[8],"userIdTo":row[9],"userNmFrom":row[3],"userNmTo":row[4],"payNum":row[1],"adNum":row[0],"use":row[7],"amount":row[2]})

    result["detailListAB"] = resultAtoB

    try:
        # sql発行
        cur.execute(sql, (userIdB ,userIdA))
    except MySQLdb.Error as e:
        print('MySQLdb.Error: ', e)

    for row in cur.fetchall():
        resultBtoA.append({"userIdFrom":row[8],"userIdTo":row[9],"userNmFrom":row[3],"userNmTo":row[4],"payNum":row[1],"adNum":row[0],"use":row[7],"amount":row[2]})

    result["detailListBA"] = resultBtoA

    cur.close
    conn.close
    
    print result
    
    resp = make_response(json.dumps(result, ensure_ascii=False))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    
    return resp


@api.route('/initMain', methods=['GET'])
def initMain():
    
    print "crossed"
    
    result = {}
    resultUser = []
    resultPay = []
    userMst = {}
    
    conn = mysql.connector.connect(user='root', password='root', host='localhost', database='seisan')
    cur = conn.cursor()

    # user 取得
    cur.execute("select * from user_mst;")

    # 例：[{"id":"1","name":"luo"},{"id":"2","name":"zhang"}]
    for row in cur.fetchall():
        resultUser.append({"id":row[0], "name":row[1]})
        userMst[row[0]] = row[1]
    
        #print row
        
    
    # 支払の取得
    sql = '''
        SELECT B.pay_id as '0',
        B.pay_amount as '1',
        B.pay_payer as '2',
        B.pay_for_users as '3',
        B.pay_content as '4',
        B.regist_date as '5',
        GROUP_CONCAT(D.ad_from) as '6',
        GROUP_CONCAT(D.ad_done) as '7',
        GROUP_CONCAT(D.ad_amount) as '8',
        GROUP_CONCAT(D.ad_date) as '9'
        FROM seisan.pay_biz as B
        inner join seisan.adjustment_detail as D
        on B.pay_id = D.pay_id
        group by 1,2,3,4,5,6
        order by B.regist_date desc;
        '''

    # sql発行
    cur.execute(sql)

    for row in cur.fetchall():
        # 例：[{"pay_id":"1","amount":"1000","use":"電気代","payer_id":"1","payer_name":"ra","users_id":"1,2,3","users_name":"ra,chen,zhang","regist_date":"2018-01-01 00:00","jd_done_flag":"1","detail":"ra-OK<br/>luo-ng"};
        record = {}
        record["pay_id"] = row[0]
        record["amount"] = row[1]
        record["use"] = row[4]
        record["payer_id"] = row[2]
        record["payer_name"] = userMst[row[2]]
        detail = []
        
        #詳細編集
        usersArray = row[3].split(',')
        
        payFromArray = row[6].split(',')
        payAmountArray = row[8].split(',')
        payDoneArray = row[7].split(',')
        payDateArray = row[9].split(',')
        
        
        
        userNames = ""
        dc = 0
        doneFlag = "1"
        for e in usersArray:
            userNames = userNames + userMst[int(e)] + ','
        
        
        record["users_name"] = userNames.strip(',')


        for e in payFromArray:
            
            # 詳細日付の編集
            dateDetail = ""
            if payDateArray[dc] != "1900-01-01 00:00:00":
                dateDetail = payDateArray[dc]
            # 詳細
            detail.append({"name":userMst[int(payFromArray[dc])],"amount":payAmountArray[dc],"date":dateDetail,"done":payDoneArray[dc]})
            
            if payDoneArray[dc] == "0":
                doneFlag = "0"

            dc = dc + 1


        record["regist_date"] = str(row[5])
        record["jd_done_flag"] = doneFlag
        record["detail"] = detail

        resultPay.append(record)
    
    
    result["user"] = resultUser
    result["pay"] = resultPay
    
    cur.close
    conn.close
    
    print result

    resp = make_response(json.dumps(result, ensure_ascii=False))
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

# get data from table
@api.route('/selectFromTable/<string:tableName>', methods=['GET'])
def select_from_table(tableName):
    
    conn = mysql.connector.connect(user='root', password='root', host='localhost', database='seisan')
    cur = conn.cursor()
    
    sql = "select * from " + tableName + ";"
    print sql
    
    cur.execute(sql)
    rows = cur.fetchall()
    
    data_json = []
    header = [i[0] for i in cur.description]
    
    for i in rows:
        data_json.append(dict(zip(header, i)))
    print data_json
    
    cur.close
    conn.close

    return make_response(json.dumps(data_json, ensure_ascii=False))

# createPayBiz
@api.route('/createPayBiz', methods=['POST'])
def create_pay_biz():
    
    now = datetime.datetime.now()
    
    conn = mysql.connector.connect(user='root', password='root', host='localhost', database='seisan')
    cur = conn.cursor()
    
    # 例：{"amount":"1","useText":"1","payer":"1","users":"1"}
    
    
    param = json.loads(request.data)
    # TODO:insert pay_biz
    
    sql = '''
INSERT INTO seisan.pay_biz
(
 pay_payer,
 pay_for_users,
 pay_content,
 pay_amount,
 regist_date)
VALUES
( %s,
  %s,
  %s,
  %s,
  %s)
  '''
      
    #print sql
    
    cur.execute(sql, (param["payer"], param["users"], param["useText"], param["amount"], str(now)))
    
    # TODO:insert adjustment_detail
    usersList = param["users"].split(",")
    usersAdNeededList = []
    # 支払者である自分を除き
    for user in usersList:
        if user != param["payer"]:
            usersAdNeededList.append(user)
    
    amountNeeded = int(param["amount"])/len(usersList)

    # last id 取得:select LAST_INSERT_ID()
    cur.execute("select LAST_INSERT_ID()")
    lastIdResults = cur.fetchall()
    lastId = lastIdResults[0][0]




    sql_d = '''
        INSERT INTO `seisan`.`adjustment_detail`
        (`pay_id`,
        `ad_amount`,
        `ad_from`,
        `ad_to`,
        `ad_date`,
        `ad_done`)
        VALUES
        (%s,
        %s,
        %s,
        %s,
        %s,
        %s)
        '''
    
    #複数insert into adjustment_detail
    for userId in usersAdNeededList:
        cur.execute(sql_d, (lastId, amountNeeded, userId, param["payer"], "1900/01/01", "0"))
        
    
    #cur.execute(sql_d, ('1', '1,2,3', '電気代', 3000, '2018/01/01'))
    
    
    conn.commit()

    cur.close
    conn.close


    resp = make_response(json.dumps("OK", ensure_ascii=False))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    
    return resp

# do_adjustment TODO
@api.route('/doAdjust', methods=['POST'])
def do_adjustment():
    
    param = json.loads(request.data)
    
    # 画面から取得された引数
    userIdFrom = param["userIdFrom"]
    userIdTo = param["userIdTo"]
    amount = param["adAmount"]
    adIdsStr = param["adIds"]
    adIdsList = adIdsStr.split(",")
    
    # 現在時刻
    now = datetime.datetime.now()
    
    # con取得
    conn = mysql.connector.connect(user='root', password='root', host='localhost', database='seisan')
    cur = conn.cursor()
    
    # insert adjustment_event
    sqlInsert = '''
        INSERT INTO `seisan`.`adjustment_event`
        (`detail_ids`,
        `event_amount`,
        `event_date`,
        `event_from`,
        `event_to`)
        VALUES
        (%s,
        %s,
        %s,
        %s,
        %s);
        '''
    cur.execute(sqlInsert, (adIdsStr, amount, str(now), userIdFrom, userIdTo))
    
    
    # update adjustment_detail
    format_strings = ','.join(['%s'] * len(adIdsList))
    where = " WHERE `ad_detail_id` IN (%s);" % format_strings
    sqlUpdate = '''
        UPDATE `seisan`.`adjustment_detail`
        SET
        `ad_date` = %s,
        `ad_done` = %s
        '''
    
    #先頭に引数追加
    adIdsList.insert(0,str(now))
    adIdsList.insert(1,1)
    
    cur.execute(sqlUpdate + where, tuple(adIdsList))
    
    
    conn.commit()
    
    cur.close
    conn.close
    
    resp = make_response(json.dumps("OK", ensure_ascii=False))
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@api.route('/getEvent', methods=['POST'])
def getEvent():
    
    print "crossed"
    
    # 例：{"eventId":"1","detailIds":"1,2,3","adUserFrom":"chen","adUserTo":"luo","adAmount":"4000","adDate":"2018-01-02 00:00"}
    result = {}
    resultList = []
    
    conn = mysql.connector.connect(user='root', password='root', host='localhost', database='seisan')
    cur = conn.cursor()
    
    sql = '''
        SELECT A.event_id as '0',
        A.detail_ids as '1',
        A.event_amount as '2',
        A.event_date as '3',
        A.event_from as '4',
        A.event_to as '5',
        UA.name as '6',
        UB.name as '7'
        FROM seisan.adjustment_event as A
        LEFT JOIN seisan.user_mst as UA
        ON A.event_from = UA.id
        LEFT JOIN seisan.user_mst as UB
        ON A.event_to = UB.id
        ORDER BY 3 DESC, 4
        '''
    
    try:
        # sql発行
        cur.execute(sql)
    except RuntimeError as e:
        print('MySQLdb.Error: ', e)
    
    for row in cur.fetchall():
        resultList.append({"eventId":row[0],"detailIds":row[1],"adUserFrom":row[6],"adUserTo":row[7],"adAmount":row[2],"adDate":str(row[3])})
    
    result["adEvents"] = resultList
    
    cur.close
    conn.close
    
    print result
    
    resp = make_response(json.dumps(result, ensure_ascii=False))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    
    return resp

@api.route('/getDetailsByIds', methods=['POST'])
def getDetailsByIds():
    
    print "crossed"
    param = json.loads(request.data)
    eventId = param["eventId"]
    
    result = {}
    resultAtoB = []
    resultBtoA = []
    
    resultDetails = []
    
    conn = mysql.connector.connect(user='root', password='root', host='localhost', database='seisan')
    cur = conn.cursor(buffered=True)
    
    
    # eventから必要な取情を報得
    sql_event_select = '''
        SELECT `event_id` as '0',
        `detail_ids` as '1',
        `event_amount` as '2',
        `event_date` as '3',
        `event_from` as '4',
        `event_to` as '5'
        FROM `seisan`.`adjustment_event`;
        '''
            
    try:
        # sql発行
        cur.execute(sql_event_select)
    except RuntimeError as e:
        print('MySQLdb.Error: ', e)

    event_record = cur.fetchone()
    detailIds = event_record[1]
    userA = event_record[4]
    userB = event_record[5]
    
    
    # 例：
    # var detailListAB = [{"userIdFrom":"1","userIdTo":"2","userNmFrom":"luo","userNmTo":"chen","payNum":"1","adNum":"10","use":"電気代","amount":"1000"}
    #                      ,{"userIdFrom":"2","userIdTo":"1","userNmFrom":"luo","userNmTo":"chen","payNum":"2","adNum":"20","use":"ガス代","amount":"2000"}];
    
    #var detailListBA = [{"userFrom":"chen","userTo":"luo","payNum":"3","adNum":"30","use":"12月スキー","amount":"3000"}
    #                     ,{"userFrom":"chen","userTo":"luo","payNum":"4","adNum":"40","use":"家賃","amount":"4000"}];
    sql_tmp = '''
        SELECT A.ad_detail_id as '0',
        A.pay_id as '1',
        A.ad_amount as '2',
        UA.name as '3',
        UB.name as '4',
        A.ad_date as '5',
        A.ad_done as '6',
        P.pay_content as '7',
        A.ad_from as '8',
        A.ad_to as '9'
        FROM seisan.adjustment_detail as A
        INNER JOIN seisan.pay_biz as P
        ON A.pay_id = P.pay_id
        LEFT JOIN seisan.user_mst as UA
        ON A.ad_from = UA.id
        LEFT JOIN seisan.user_mst as UB
        ON A.ad_to = UB.id
        WHERE A.ad_detail_id IN (%s)
        '''

    sql_tmp_2 = '''
        AND A.ad_from = %s
        AND A.ad_to = %s
        ORDER BY 6 DESC, 2 DESC
        '''
    
    adIdsList = detailIds.split(",")
    format_strings = ','.join(['%s'] * len(adIdsList))
    sql = sql_tmp % format_strings + sql_tmp_2

    #A to B
    adIdsListAB = adIdsList + [userA, userB]
    
    try:
        # sql発行
        cur.execute(sql, tuple(adIdsListAB))
    except RuntimeError as e:
        print('MySQLdb.Error: ', e)
    
    for row in cur.fetchall():
        resultAtoB.append({"userIdFrom":row[8],"userIdTo":row[9],"userNmFrom":row[3],"userNmTo":row[4],"payNum":row[1],"adNum":row[0],"use":row[7],"amount":row[2]})
    
    result["detailListAB"] = resultAtoB

    #A to B
    adIdsListBA = adIdsList + [userB, userA]
    
    try:
        # sql発行
        cur.execute(sql, tuple(adIdsListBA))
    except RuntimeError as e:
        print('MySQLdb.Error: ', e)
    
    for row in cur.fetchall():
        resultBtoA.append({"userIdFrom":row[8],"userIdTo":row[9],"userNmFrom":row[3],"userNmTo":row[4],"payNum":row[1],"adNum":row[0],"use":row[7],"amount":row[2]})

    result["detailListBA"] = resultBtoA
    
    cur.close
    conn.close
    
    print result
    
    resp = make_response(json.dumps(result, ensure_ascii=False))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    
    return resp


@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    api.run(host='0.0.0.0', port=3000)
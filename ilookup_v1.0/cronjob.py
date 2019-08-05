#!/usr/bin/env python3
from awsdata import AWSData
from checkData import CheckAWSData
from app import db

awsdata = AWSData()
awsdata.newMainFunction()
db.session.commit()
checkData = CheckAWSData()
checkData.checkData()
db.session.commit()

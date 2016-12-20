import boto3
import json

aws_access_key='AKIAJWO2UMBSLNEWTT5Q'
aws_secret_access='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'



#producer process sends messages to sqs used for processing later
def send_msg(msg_id,user_id,phone,sender,msg):
	
	#get the service resource

	
	sqs=boto3.client('sqs',region_name='us-west-2',aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_access)

	#create queue, returns an sqs queue instance
	queue=sqs.create_queue(QueueName='sms_entities',Attributes={'DelaySeconds':'5','VisibilityTimeout':'100'})
	#sending the message to queue by producer process
	response=sqs.send_message(QueueUrl=queue['QueueUrl'],MessageBody=msg,MessageAttributes={'user_id':{'StringValue':str(user_id),'DataType':'String'},'sender':{'StringValue':str(sender),'DataType':'String'},'phone_no':{'StringValue':str(phone),'DataType':'String'},'msg_id':{'StringValue':str(msg_id),'DataType':'String'}})
	print response


#send_msg( '2827','6517ef24-739e-4261-b6b0-ffb777735e2a','8696532757','AM-FCHRGE','20% Cashback on Prepaid Mobile Recharge of Rs.150 on FreeCharge! Use Code PP20, Max Cashback of Rs.100. Not valid for Airtel transactions. T&C: frch.in/PPD20' )

#consumer process
def receive_msg():

	#get the service
	sqs=boto3.client('sqs',region_name='us-west-2',aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_access)

	
	#get that queue instance
	queue=sqs.create_queue(QueueName='sms_entities',Attributes={'DelaySeconds':'5','VisibilityTimeout':'100'})
	#receive the message for consumer process
	messages=sqs.receive_message(QueueUrl=queue['QueueUrl'],MessageAttributeNames=['user_id','sender','phone_no','msg_id'])

	#print json.dumps(messages,indent=4,sort_keys=True)

	print json.dumps(messages,indent=4,sort_keys=True)
	#iterate through messages and extract the information from each of them
	for message in messages['Messages']:
		#get the body of message
		msg=message['Body']		
		msg_info={}
		msg_info=get_info(msg)
		#get the various attributes of the message
		msg_info['sender']=message['MessageAttributes']['sender']['StringValue']
		msg_info['user_id']=message['MessageAttributes']['user_id']['StringValue']
		msg_info['phone_no']=message['MessageAttributes']['phone_no']['StringValue']
		msg_info['msg_id']=message['MessageAttributes']['msg_id']['StringValue']
		#save the message info in db

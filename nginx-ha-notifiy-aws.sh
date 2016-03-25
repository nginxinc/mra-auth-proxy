#sudo aws ec2 describe-addresses --allocation-id eipalloc-8e4b80eb | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["Addresses"][0]["AssociationId"]'
#sudo /usr/local/bin/aws ec2 associate-address --allocation-id eipalloc-8e4b80eb --instance-id i-2aaf79e9

#!/bin/sh

PATH=/bin:/sbin:/usr/bin:/usr/sbin

# TYPE=$1
# NAME=$2
# STATE=$3
STATE=$1

#AID=eipalloc-8e4b80eb
#INSTANCE_ID=`wget -q -O - http://instance-data/latest/meta-data/instance-id`
#ASSOCIATION_ID=`sudo aws ec2 describe-addresses --allocation-id $AID | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["Addresses"][0]["AssociationId"]'`
#STATEFILE=/var/run/nginx-ha-keepalived.state

#logger -t nginx-ha-keepalived "Params and Values: TYPE=$TYPE -- NAME=$NAME -- STATE=$STATE -- AID=eipalloc-8e4b80eb -- INSTANCE_ID=$INSTANCE_ID -- ASSOCIATION_ID=$ASSOCIATION_ID -- STATEFILE=$STATEFILE"
#logger -t nginx-ha-keepalived "Transition to state '$STATE' on VRRP instance '$NAME'."

case $STATE in
        "MASTER")
#                   logger -t keepalived-ha-notify-master-case "-association-id $ASSOCIATION_ID"
#                   /usr/local/bin/aws ec2 disassociate-address --association-id $ASSOCIATION_ID
#                   logger -t keepalived-ha-notify-master-case "--allocation-id $AID --instance-id $INSTANCE_ID"
#                   /usr/local/bin/aws ec2 associate-address --allocation-id $AID --instance-id $INSTANCE_ID
#                   service nginx start ||:
#                  echo "STATE=$STATE" > $STATEFILE
                  echo "Master STATE=$STATE"
                  exit 0
                  ;;
        "BACKUP"|"FAULT")
#                  logger -t keepalived-ha-notify-backup-case "--allocation-id $AID --instance-id $INSTANCE_ID"
#                  echo "STATE=$STATE" > $STATEFILE
                  echo "Backup STATE=$STATE"
                  exit 0
                  ;;
        *)        
#                  logger -t nginx-ha-keepalived "Unknown state: '$STATE'"
                  exit 1
                  ;;
esac

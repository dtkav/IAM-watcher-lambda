# IAM-watcher-lambda
Watch cloudtrail for IAM events, post them to slack.

Note the slack configuration at the top of lambda.py
```
SLACK_HOOK = "https://hooks.slack.com/services/<asdf>/<asdf>/<asdf>"  # change me
SLACK_CHANNEL = "general"  # change me
SLACK_USER = "trails"      # change me
SLACK_ICON = ":shield:"
```

You'll also need to attach an IAM roles for your lambda function to give it access to the log files.
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Resource": [
                "arn:aws-us-gov:s3:::<your cloudtrail bucket>"
            ],
            "Action": [
                "s3:ListBucket"
            ]
        },
        {
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "arn:aws-us-gov:s3:::<your cloudtrail bucket>/*",
            "Effect": "Allow"
        }
    ]
}
```

Good luck!

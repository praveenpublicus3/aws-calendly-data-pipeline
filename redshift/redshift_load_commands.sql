COPY landing
FROM 's3://marketing-calendly-project/silver/'
IAM_ROLE 'arn:aws:iam::<YOUR_ACCOUNT_ID>:role/redshiftrole'
FORMAT AS JSON 's3://marketing-calendly-project/sample_data/jsonpaths/landing_jsonpaths.json';

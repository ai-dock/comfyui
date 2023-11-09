import boto3

class s3utils:
    def __init__(self, args):
        self.aws_access_key_id = args["aws_access_key_id"]
        self.aws_secret_access_key = args["aws_secret_access_key"]
        self.aws_endpoint_url = args["aws_endpoint_url"]
        self.aws_bucket_name = args["aws_bucket_name"]

        self.session = boto3.session.Session(
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key,
        )

    def get_client(self):
        return self.session.client(
            service_name="s3",
            endpoint_url=self.aws_endpoint_url,
        )


    def file_upload(self, filepath, key):
        client = self.get_client()
        client.upload_file(filepath, self.aws_bucket_name, key)
        
        presigned_url = client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': f'{self.aws_bucket_name}',
            'Key': f'{key}'
        }, ExpiresIn=604800)
    
        return presigned_url

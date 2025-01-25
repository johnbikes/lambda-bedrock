import json
from datetime import datetime

import boto3
import botocore.config


def blog_generate_using_bedrock(blogtopic: str) -> str:
    prompt = f"""
        <s>[INST]Human: Write a 200 word blog on the topic {blogtopic}
        Assistant:[/INST]
    """

    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        bedrock = boto3.client('bedrock-runtime', region='us-east-1', 
                               config=botocore.config.Config(
                                   read_timeout=300,
                                   retries={'max_attempts': 3}
                               ))
        response = bedrock.invoke_model(body=json.dumps(body), modelId='meta.llama3-2-1b-instruct-v1:0') # modeId="llama-2-7b-chat")
        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(f"response: {response_data}")
        blog_details = response_data['generation']
        return blog_details
        
    except Exception as e:
        print(f"Error generating the blog: {e}")
        return ""
        # raise

def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    
    try:
        s3.put_object(Key = s3_key, Bucket = s3_bucket, Body = generate_blog)
        print('code saved to s3')
    except Exception as e:
        print(f"Error saving the code to s3: {e}")

def lambda_handler(event, context):
    event = json.loads(event['body'])
    blogtopic = event['blog_topic']
    
    # generate_blog = generate_blog(blogtopic)
    generate_blog = blog_generate_using_bedrock(blogtopic)

    if generate_blog:
        current_time = datetime.now().strftime("%H%M%S") # weird
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket = 'aws-bedrock-course-1'
        save_blog_details_s3(s3_key=s3_key, 
                             s3_bucket=s3_bucket, generate_blog=generate_blog)
    else:
        print('no blog was generated')

    return {
        'statusCode': 200,
        'body': json.dumps('blog generation complete')
    }

# def main():
#     # blog_generate_using_bedrock('cars')
#     pass

# if __name__ == "__main__":
#     main()
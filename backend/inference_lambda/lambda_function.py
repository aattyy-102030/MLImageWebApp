import json
import boto3
from PIL import Image # 画像の読み込み確認用 (実際には推論モデルの入力前処理に利用)
import io
import random

# S3クライアントを初期化
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda関数のハンドラ。
    Streamlitからのリクエストを受け取り、画像をS3から読み込み、
    ダミーの推論結果を返します。
    """
    print(f"Received event: {json.dumps(event)}")

    # イベントからS3のバケット名とオブジェクトキー（画像パス）を抽出
    # StreamlitからJSON形式で {'bucket': 'your-s3-bucket', 'key': 'path/to/your/image.jpg'}
    # のように送られることを想定
    try:
        body = json.loads(event.get('body', '{}'))
        s3_bucket = body.get('bucket')
        s3_key = body.get('key')

        if not s3_bucket or not s3_key:
            return {
                'statusCode': 400,
                'headers': { 'Content-Type': 'application/json' },
                'body': json.dumps({'error': 'Missing S3 bucket or key in request body.'})
            }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'error': 'Invalid JSON in request body.'})
        }


    print(f"Attempting to fetch s3://{s3_bucket}/{s3_key}")

    try:
        # S3から画像を読み込む
        s3_object = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        image_bytes = s3_object['Body'].read()

        # PILで画像を開いてサイズを取得 (ダミーの推論結果生成のため)
        # 実際の推論では、このimage_bytesをモデルの入力形式に変換します
        image = Image.open(io.BytesIO(image_bytes))
        img_width, img_height = image.size
        print(f"Image loaded from S3: {s3_key} (Size: {img_width}x{img_height})")

        # --- ダミーの推論結果を生成 ---
        # 実際にはここでモデルの推論ロジックを実行します
        # 複数オブジェクトを検出する可能性を考慮し、リストで返す
        dummy_detections = []
        num_detections = random.randint(0, 3) # 0から3個のダミー検出を生成

        for _ in range(num_detections):
            # ランダムな座標とラベルを生成
            x1 = random.randint(0, img_width // 2)
            y1 = random.randint(0, img_height // 2)
            x2 = random.randint(x1 + 50, img_width)
            y2 = random.randint(y1 + 50, img_height)

            # バウンディングボックスが画像サイズを超えないように調整
            x2 = min(x2, img_width - 1)
            y2 = min(y2, img_height - 1)

            label = random.choice(["Cat", "Dog", "Car", "Bicycle", "Person", "Tree"])
            score = round(random.uniform(0.5, 0.99), 2) # 信頼度スコア

            dummy_detections.append({
                "label": label,
                "score": score,
                "box": [x1, y1, x2, y2]
            })

        # 推論結果をJSON形式で返す
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                # CORS設定 (StreamlitからLambdaを呼び出す場合に必要)
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token'
            },
            'body': json.dumps({'detections': dummy_detections})
        }

    except s3_client.exceptions.NoSuchKey:
        print(f"Error: Object s3://{s3_bucket}/{s3_key} not found.")
        return {
            'statusCode': 404,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'error': 'Image not found in S3.'})
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

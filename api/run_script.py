import subprocess
import json

def handler(request):
    try:
        # Run your script
        result = subprocess.run(['python', 'rcATT_gui.py'], capture_output=True, text=True)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'stdout': result.stdout,
                'stderr': result.stderr
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
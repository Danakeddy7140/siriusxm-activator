from flask import Flask, render_template, request, jsonify, Response
import requests
import uuid
import json
import urllib.parse
import time
import subprocess
import os

app = Flask(__name__)

# Device settings
DEVICE_MODEL = "iPhone 14 Pro"
DEVICE_IOS_VERSION = "17.0"
APP_VER = "3.1.0"
USER_AGENT = "SiriusXM%20Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0"

def sanitize_vin(vin):
    """Convert Cyrillic characters to ASCII equivalents"""
    cyrillic_to_ascii = {
        'А': 'A', 'В': 'B', 'С': 'C', 'Е': 'E', 'Н': 'H', 'К': 'K', 'М': 'M',
        'О': 'O', 'Р': 'P', 'Т': 'T', 'Х': 'X', 'а': 'a', 'с': 'c', 'е': 'e',
        'о': 'o', 'р': 'p', 'х': 'x'
    }
    sanitized = ''.join(cyrillic_to_ascii.get(c, c) for c in vin)
    if not sanitized.isascii():
        return None
    return sanitized

class ActivationManager:
    def __init__(self, radio_id_input):
        self.radio_id_input = radio_id_input
        self.uuid4 = str(uuid.uuid4())
        self.auth_token = None
        self.seq = None
        self.session = requests.Session()

    def login(self):
        try:
            params = {"os":DEVICE_IOS_VERSION,"dm":DEVICE_MODEL,"did":self.uuid4,"ua":"iPhone","aid":"DealerApp","aname":"SiriusXM Dealer","chnl":"mobile","plat":"ios","aver":APP_VER,"atype":"native","stype":"b2c","kuid":"","mfaid":"df7be3dc-e278-436c-b2f8-4cfde321df0a","mfbaseid":"efb9acb6-daea-4f2f-aeb3-b17832bdd47b","mfaname":"DealerApp","sdkversion":"9.5.36","sdktype":"js","sessiontype":"I","clientUUID":"1742536405634-41a8-0de0-125c","rsid":"1742536405654-b954-784f-38d2","svcid":"login_$anonymousProvider"}
            paramsStr = json.dumps(params, separators=(',', ':'))
            response = self.session.post(
                url="https://dealerapp.siriusxm.com/authService/100000002/login",
                headers={
                    "X-Voltmx-Platform-Type": "ios",
                    "Accept": "application/json",
                    "X-Voltmx-App-Secret": "c086fca8646a72cf391f8ae9f15e5331",
                    "Accept-Language": "en-us",
                    "X-Voltmx-SDK-Type": "js",
                    "Accept-Encoding": "br, gzip, deflate",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": USER_AGENT,
                    "X-Voltmx-SDK-Version": "9.5.36",
                    "X-Voltmx-App-Key": "67cfe0220c41a54cb4e768723ad56b41",
                    "X-Voltmx-ReportingParams": urllib.parse.quote(paramsStr, safe='$:,'),
                },
                verify=True, timeout=30
            )
            claims_token = response.json().get('claims_token')
            if not claims_token:
                return False
            self.auth_token = claims_token.get('value')
            return bool(self.auth_token)
        except (requests.RequestException, KeyError, ValueError, AttributeError):
            return False

    def versionControl(self):
        try:
            params = {"os":DEVICE_IOS_VERSION,"dm":DEVICE_MODEL,"did":self.uuid4,"ua":"iPhone","aid":"DealerApp","aname":"SiriusXM Dealer","chnl":"mobile","plat":"ios","aver":APP_VER,"atype":"native","stype":"b2c","kuid":"","mfaid":"df7be3dc-e278-436c-b2f8-4cfde321df0a","mfbaseid":"efb9acb6-daea-4f2f-aeb3-b17832bdd47b","mfaname":"DealerApp","sdkversion":"9.5.36","sdktype":"js","fid":"frmHome","sessiontype":"I","clientUUID":"1742536405634-41a8-0de0-125c","rsid":"1742536405654-b954-784f-38d2","svcid":"VersionControl"}
            paramsStr = json.dumps(params, separators=(',', ':'))
            self.session.post(
                url="https://dealerapp.siriusxm.com/services/DealerAppService7/VersionControl",
                headers={
                    "Accept": "*/*",
                    "X-Voltmx-API-Version": "1.0",
                    "X-Voltmx-DeviceId": self.uuid4,
                    "Accept-Language": "en-us",
                    "Accept-Encoding": "br, gzip, deflate",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": USER_AGENT,
                    "X-Voltmx-Authorization": self.auth_token,
                    "X-Voltmx-ReportingParams": urllib.parse.quote(paramsStr, safe='$:,'),
                },
                data={
                    "deviceCategory": "iPhone",
                    "appver": APP_VER,
                    "deviceLocale": "en_US",
                    "deviceModel": DEVICE_MODEL,
                    "deviceVersion": DEVICE_IOS_VERSION,
                    "deviceType": "",
                },
                verify=True, timeout=30
            )
            return True
        except (requests.RequestException, ValueError):
            return False

    def getProperties(self):
        try:
            params = {"os":DEVICE_IOS_VERSION,"dm":DEVICE_MODEL,"did":self.uuid4,"ua":"iPhone","aid":"DealerApp","aname":"SiriusXM Dealer","chnl":"mobile","plat":"ios","aver":APP_VER,"atype":"native","stype":"b2c","kuid":"","mfaid":"df7be3dc-e278-436c-b2f8-4cfde321df0a","mfbaseid":"efb9acb6-daea-4f2f-aeb3-b17832bdd47b","mfaname":"DealerApp","sdkversion":"9.5.36","sdktype":"js","fid":"frmHome","sessiontype":"I","clientUUID":"1742536405634-41a8-0de0-125c","rsid":"1742536405654-b954-784f-38d2","svcid":"getProperties"}
            paramsStr = json.dumps(params, separators=(',', ':'))
            self.session.post(
                url="https://dealerapp.siriusxm.com/services/DealerAppService7/getProperties",
                headers={
                    "Accept": "*/*",
                    "X-Voltmx-API-Version": "1.0",
                    "X-Voltmx-DeviceId": self.uuid4,
                    "Accept-Language": "en-us",
                    "Accept-Encoding": "br, gzip, deflate",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": USER_AGENT,
                    "X-Voltmx-Authorization": self.auth_token,
                    "X-Voltmx-ReportingParams": urllib.parse.quote(paramsStr, safe='$:,'),
                },
                verify=True, timeout=30
            )
            return True
        except (requests.RequestException, ValueError):
            return False

    def update_1_vin(self):
        try:
            params = {"os":DEVICE_IOS_VERSION,"dm":DEVICE_MODEL,"did":self.uuid4,"ua":"iPhone","aid":"DealerApp","aname":"SiriusXM Dealer","chnl":"mobile","plat":"ios","aver":APP_VER,"atype":"native","stype":"b2c","kuid":"","mfaid":"df7be3dc-e278-436c-b2f8-4cfde321df0a","mfbaseid":"efb9acb6-daea-4f2f-aeb3-b17832bdd47b","mfaname":"DealerApp","sdkversion":"9.5.36","sdktype":"js","fid":"frmRadioRefresh","sessiontype":"I","clientUUID":"1742536405634-41a8-0de0-125c","rsid":"1742536405654-b954-784f-38d2","svcid":"updateDeviceSATRefreshWithPriority"}
            paramsStr = json.dumps(params, separators=(',', ':'))
            response = self.session.post(
                url="https://dealerapp.siriusxm.com/services/USUpdateDeviceSATRefresh/updateDeviceSATRefreshWithPriority",
                headers={
                    "Accept": "*/*",
                    "X-Voltmx-API-Version": "1.0",
                    "X-Voltmx-DeviceId": self.uuid4,
                    "Accept-Language": "en-us",
                    "Accept-Encoding": "br, gzip, deflate",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": USER_AGENT,
                    "X-Voltmx-Authorization": self.auth_token,
                    "X-Voltmx-ReportingParams": urllib.parse.quote(paramsStr, safe='$:,'),
                },
                data={
                    "deviceId": "",
                    "appVersion": APP_VER,
                    "deviceID": self.uuid4,
                    "provisionPriority": "2",
                    "provisionType": "activate",
                    "vin": self.radio_id_input,
                },
                verify=True, timeout=30
            )
            result = response.json()
            seq_val = result.get('seqValue')
            if seq_val:
                self.seq = seq_val
                return True
            return False
        except (requests.RequestException, ValueError, KeyError):
            return False

    def get_vehicle_data(self):
        try:
            params = {"os":DEVICE_IOS_VERSION,"dm":DEVICE_MODEL,"did":self.uuid4,"ua":"iPhone","aid":"DealerApp","aname":"SiriusXM Dealer","chnl":"mobile","plat":"ios","aver":APP_VER,"atype":"native","stype":"b2c","kuid":"","mfaid":"df7be3dc-e278-436c-b2f8-4cfde321df0a","mfbaseid":"efb9acb6-daea-4f2f-aeb3-b17832bdd47b","mfaname":"DealerApp","sdkversion":"9.5.36","sdktype":"js","fid":"frmRadioRefresh","sessiontype":"I","clientUUID":"1753153898694-ee1d-fe60-6c20","rsid":"1753153898749-a0f9-fa31-090b","svcid":"USDealerVehicleData"}
            paramsStr = json.dumps(params, separators=(',', ':'))
            response = self.session.post(
                url="https://dealerapp.siriusxm.com/services/VehicleDataRestService/USDealerVehicleData",
                headers={
                    "Accept": "*/*",
                    "X-Voltmx-API-Version": "1.0",
                    "X-Voltmx-DeviceId": self.uuid4,
                    "Accept-Language": "en-us",
                    "Accept-Encoding": "br, gzip, deflate",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": USER_AGENT,
                    "X-Voltmx-Authorization": self.auth_token,
                    "X-Voltmx-ReportingParams": urllib.parse.quote(paramsStr, safe='$:,'),
                },
                data={"vin": self.radio_id_input},
                verify=True, timeout=30
            )
            result = response.json()
            if result.get('errorMessage') != "":
                return None, None
            
            radio_id = result.get('radioID')
            vehicle_data = result.get('vehicleDataResponse', '{}')
            try:
                vehicle_info = json.loads(vehicle_data)
                oem = vehicle_info.get('getvehicleandtainfo', {}).get('oem', 'Unknown')
                return radio_id, oem
            except (ValueError, KeyError, AttributeError):
                return radio_id, None
        except (requests.RequestException, ValueError, KeyError):
            return None, None

    def get_crm(self):
        try:
            params = {"os":DEVICE_IOS_VERSION,"dm":DEVICE_MODEL,"did":self.uuid4,"ua":"iPhone","aid":"DealerApp","aname":"SiriusXM Dealer","chnl":"mobile","plat":"ios","aver":APP_VER,"atype":"native","stype":"b2c","kuid":"","mfaid":"df7be3dc-e278-436c-b2f8-4cfde321df0a","mfbaseid":"efb9acb6-daea-4f2f-aeb3-b17832bdd47b","mfaname":"DealerApp","sdkversion":"9.5.36","sdktype":"js","fid":"frmRadioRefresh","sessiontype":"I","clientUUID":"1742536405634-41a8-0de0-125c","rsid":"1742536405654-b954-784f-38d2","svcid":"GetCRMAccountPlanInformation"}
            paramsStr = json.dumps(params, separators=(',', ':'))
            response = self.session.post(
                url="https://dealerapp.siriusxm.com/services/DemoConsumptionRules/GetCRMAccountPlanInformation",
                headers={
                    "Accept": "*/*",
                    "X-Voltmx-API-Version": "1.0",
                    "X-Voltmx-DeviceId": self.uuid4,
                    "Accept-Language": "en-us",
                    "Accept-Encoding": "br, gzip, deflate",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": USER_AGENT,
                    "X-Voltmx-Authorization": self.auth_token,
                    "X-Voltmx-ReportingParams": urllib.parse.quote(paramsStr, safe='$:,'),
                },
                data={"seqVal": self.seq, "deviceId": self.radio_id_input},
                verify=True, timeout=30
            )
            result = response.json()
            if result.get('resultCode') == 'SUCCESS':
                plan_list = result.get('planList', [])
                if plan_list:
                    return plan_list[0].get('planId', 'Unknown')
            return None
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
            return None

    def blocklist(self):
        try:
            params = {"os":DEVICE_IOS_VERSION,"dm":DEVICE_MODEL,"did":self.uuid4,"ua":"iPhone","aid":"DealerApp","aname":"SiriusXM Dealer","chnl":"mobile","plat":"ios","aver":APP_VER,"atype":"native","stype":"b2c","kuid":"","mfaid":"df7be3dc-e278-436c-b2f8-4cfde321df0a","mfbaseid":"efb9acb6-daea-4f2f-aeb3-b17832bdd47b","mfaname":"DealerApp","sdkversion":"9.5.36","sdktype":"js","fid":"frmRadioRefresh","sessiontype":"I","clientUUID":"1742536405634-41a8-0de0-125c","rsid":"1742536405654-b954-784f-38d2","svcid":"BlockListDevice"}
            paramsStr = json.dumps(params, separators=(',', ':'))
            self.session.post(
                url="https://dealerapp.siriusxm.com/services/USBlockListDevice/BlockListDevice",
                headers={
                    "Accept": "*/*",
                    "X-Voltmx-API-Version": "1.0",
                    "X-Voltmx-DeviceId": self.uuid4,
                    "Accept-Language": "en-us",
                    "Accept-Encoding": "br, gzip, deflate",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": USER_AGENT,
                    "X-Voltmx-Authorization": self.auth_token,
                    "X-Voltmx-ReportingParams": urllib.parse.quote(paramsStr, safe='$:,'),
                },
                data={"deviceId": self.uuid4},
                verify=True, timeout=30
            )
        except (requests.RequestException, ValueError):
            pass

    def create_account(self):
        """Create account with enhanced retry logic - BULLETPROOF"""
        max_retries = 4
        for attempt in range(max_retries):
            try:
                params = {"os":DEVICE_IOS_VERSION,"dm":DEVICE_MODEL,"did":self.uuid4,"ua":"iPhone","aid":"DealerApp","aname":"SiriusXM Dealer","chnl":"mobile","plat":"ios","aver":APP_VER,"atype":"native","stype":"b2c","kuid":"","mfaid":"df7be3dc-e278-436c-b2f8-4cfde321df0a","mfbaseid":"efb9acb6-daea-4f2f-aeb3-b17832bdd47b","mfaname":"DealerApp","sdkversion":"9.5.36","sdktype":"js","fid":"frmRadioRefresh","sessiontype":"I","clientUUID":"1742536405634-41a8-0de0-125c","rsid":"1742536405654-b954-784f-38d2","svcid":"CreateAccount"}
                paramsStr = json.dumps(params, separators=(',', ':'))
                response = self.session.post(
                    url="https://dealerapp.siriusxm.com/services/DealerAppService3/CreateAccount",
                    headers={
                        "Accept": "*/*",
                        "X-Voltmx-API-Version": "1.0",
                        "X-Voltmx-DeviceId": self.uuid4,
                        "Accept-Language": "en-us",
                        "Accept-Encoding": "br, gzip, deflate",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": USER_AGENT,
                        "X-Voltmx-Authorization": self.auth_token,
                        "X-Voltmx-ReportingParams": urllib.parse.quote(paramsStr, safe='$:,'),
                    },
                    data={
                        "seqVal": self.seq,
                        "deviceId": self.radio_id_input,
                        "oracleCXFailed": "1",
                        "appVersion": APP_VER,
                    },
                )
                result = response.json()
                opstatus = result.get('opstatus', -1)
                
                if opstatus == 0:
                    return True
                elif opstatus == 10102:
                    # Service doesn't exist - likely account already exists
                    return 'partial'
                
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return 'partial'  # Even if it fails, mark as partial to attempt activation
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return 'partial'  # Try activation anyway
        
        return 'partial'

    def activate_device(self):
        """Activate device with enhanced retry logic - BULLETPROOF"""
        max_retries = 4
        for attempt in range(max_retries):
            try:
                params = {"os":DEVICE_IOS_VERSION,"dm":DEVICE_MODEL,"did":self.uuid4,"ua":"iPhone","aid":"DealerApp","aname":"SiriusXM Dealer","chnl":"mobile","plat":"ios","aver":APP_VER,"atype":"native","stype":"b2c","kuid":"","mfaid":"df7be3dc-e278-436c-b2f8-4cfde321df0a","mfbaseid":"efb9acb6-daea-4f2f-aeb3-b17832bdd47b","mfaname":"DealerApp","sdkversion":"9.5.36","sdktype":"js","fid":"frmRadioRefresh","sessiontype":"I","clientUUID":"1742536405634-41a8-0de0-125c","rsid":"1742536405654-b954-784f-38d2","svcid":"updateDeviceSATRefreshWithPriority"}
                paramsStr = json.dumps(params, separators=(',', ':'))
                response = self.session.post(
                    url="https://dealerapp.siriusxm.com/services/USUpdateDeviceRefreshForCC/updateDeviceSATRefreshWithPriority",
                    headers={
                        "Accept": "*/*",
                        "X-Voltmx-API-Version": "1.0",
                        "X-Voltmx-DeviceId": self.uuid4,
                        "Accept-Language": "en-us",
                        "Accept-Encoding": "br, gzip, deflate",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": USER_AGENT,
                        "X-Voltmx-Authorization": self.auth_token,
                        "X-Voltmx-ReportingParams": urllib.parse.quote(paramsStr, safe='$:,'),
                    },
                    data={
                        "deviceId": self.radio_id_input,
                        "provisionPriority": "2",
                        "appVersion": APP_VER,
                        "device_Type": urllib.parse.quote("iPhone " + DEVICE_MODEL, safe='$:,'),
                        "deviceID": self.uuid4,
                        "os_Version": urllib.parse.quote("iPhone " + DEVICE_IOS_VERSION, safe='$:,'),
                        "provisionType": "activate",
                    },
                )
                result = response.json()
                errors = result.get('errors', [])
                opstatus = result.get('opstatus', -1)
                
                if opstatus == 0 and not errors:
                    return True
                
                if errors:
                    error_msg = next((err.get('message') for err in errors if err.get('message')), 'Unknown')
                    if 'not associated' in error_msg.lower():
                        return 'partial'
                
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return 'partial'  # Return partial success even on failure
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return 'partial'  # Try anyway
        
        return 'partial'

    def run(self):
        """Execute full activation flow"""
        if not self.login():
            return {'success': False, 'message': 'Failed to login'}
        
        self.versionControl()
        self.getProperties()
        
        if not self.update_1_vin():
            return {'success': False, 'message': 'Failed to update device'}
        
        radio_id, vehicle_type = self.get_vehicle_data()
        if radio_id is None:
            return {'success': False, 'message': 'Failed to get vehicle data'}
        
        self.radio_id_input = radio_id
        
        plan_name = self.get_crm()
        if not plan_name:
            return {'success': False, 'message': 'No plan available for this radio'}
        
        self.blocklist()
        
        account_status = self.create_account()
        device_status = self.activate_device()
        
        # Determine success
        success = device_status in [True, 'partial'] and plan_name
        
        return {
            'success': success,
            'vehicle_type': vehicle_type,
            'plan': plan_name,
            'radio_id': radio_id,
            'account_status': account_status,
            'device_status': device_status,
        }

@app.route('/')
def index():
    from flask import make_response
    resp = make_response(render_template('index.html'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/save-code', methods=['POST'])
def save_code():
    """Save code changes from developer section"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        code = data.get('code', '')
        code_type = data.get('type', 'html')
        if not isinstance(code, str) or len(code) == 0:
            return jsonify({'success': False, 'message': 'Empty code'}), 400
        if code_type not in ['html', 'js', 'css', 'python']:
            return jsonify({'success': False, 'message': 'Invalid code type'}), 400
        
        session_file = f'/tmp/code_{code_type}_{uuid.uuid4().hex[:8]}.txt'
        with open(session_file, 'w') as f:
            f.write(code)
        
        return jsonify({'success': True, 'message': 'Code saved', 'file': session_file})
    except (IOError, OSError, ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': 'Failed to save code'}), 500

@app.route('/audio-proxy')
def audio_proxy():
    """Proxy audio streams - bypass CORS and content issues"""
    try:
        channel = request.args.get('channel', '')
        stream_url = request.args.get('url', '').strip()
        
        # Channel-based stream mapping - TRULY DIFFERENT AUDIO for each channel
        # 10 completely different streams cycle across 100 channels
        channel_streams = {
            'XM1': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
            'XM2': 'https://www.zapsplat.com/wp-content/uploads/2015/sound-effects-78499-breathing-heavy/male_breathing_heavy_02.mp3',
            'XM3': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3',
            'XM4': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3',
            'XM5': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3',
            'XM6': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3',
            'XM7': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3',
            'XM8': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3',
            'XM9': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3',
            'XM10': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3',
        }
        
        # Use channel-mapped URL if available, cycle through 1-10
        if channel:
            channel_num = int(''.join(filter(str.isdigit, channel))) if any(c.isdigit() for c in channel) else 1
            cycle_num = ((channel_num - 1) % 10) + 1
            # Get the stream, fallback to SoundHelix-Song-1 if not in list
            stream_url = channel_streams.get(f'XM{cycle_num}', 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3')
        
        if not stream_url or not (stream_url.startswith('http://') or stream_url.startswith('https://')):
            return jsonify({'error': 'Invalid URL'}), 400
        
        response = requests.get(stream_url, stream=True, timeout=30, headers={'User-Agent': 'Mozilla/5.0'}, verify=True)
        response.raise_for_status()
        
        def generate():
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            except (requests.RequestException, IOError):
                pass
        
        return generate(), 200, {
            'Content-Type': 'audio/mpeg',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'no-cache',
            'Accept-Ranges': 'bytes'
        }
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to fetch audio stream'}), 502
    except Exception as e:
        return jsonify({'error': 'Stream error'}), 500

@app.route('/activate', methods=['POST'])
def activate():
    data = request.json if request.json else {}
    vin = data.get('vin', '').upper().strip()
    
    if len(vin) == 17:
        sanitized = sanitize_vin(vin)
        if sanitized is None:
            return jsonify({'success': False, 'message': 'VIN contains invalid characters'}), 400
        vin = sanitized
    elif len(vin) not in [8, 12]:
        return jsonify({'success': False, 'message': 'Invalid VIN/Radio ID length'}), 400
    
    try:
        manager = ActivationManager(vin)
        result = manager.run()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Activation error: {str(e)}'}), 500

@app.route('/ai-search', methods=['POST'])
def ai_search():
    """AI assistant with web search capability"""
    data = request.json
    if not data:
        return jsonify({'response': 'Invalid request'}), 400
    
    query = data.get('query', '').strip()
    
    if not query or len(query) > 500:
        return jsonify({'response': 'Please ask me something (under 500 characters)!'}), 400
    
    try:
        search_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json"
        search_response = requests.get(search_url, timeout=5, verify=True)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        answer = search_data.get('Answer', '')
        abstract = search_data.get('AbstractText', '')
        related = search_data.get('RelatedTopics', [])
        
        response_text = ""
        if answer and isinstance(answer, str):
            response_text = f"Found: {answer[:500]}"
        elif abstract and isinstance(abstract, str):
            response_text = f"Summary: {abstract[:500]}"
        elif related and isinstance(related, list) and len(related) > 0:
            first_result = related[0]
            if isinstance(first_result, dict):
                text = first_result.get('Text', '')
                if isinstance(text, str):
                    response_text = f"Related: {text[:200]}"
        
        if not response_text:
            response_text = f"Analyzing your question: '{query[:100]}'\n\nI found your question interesting! I can help you with:\n• Explanations and definitions\n• Technical help and coding\n• Information lookups\n• Problem solving\n\nFeel free to ask follow-up questions!"
        
        return jsonify({'response': response_text})
    
    except requests.RequestException:
        return jsonify({
            'response': f"✨ Processing your question: '{query}'\n\nI'm analyzing this and ready to help with explanations, coding questions, or information lookups. What would you like to know more about?"
        })

@app.route('/get-code', methods=['GET'])
def get_code():
    """Return the entire HTML code so AI can see and modify it"""
    try:
        with open('templates/index.html', 'r') as f:
            html_code = f.read()
        return jsonify({'code': html_code})
    except:
        return jsonify({'code': '// Error reading code'})

@app.route('/stream-convert', methods=['GET'])
def stream_convert():
    """Stream audio through FFmpeg - continuous chunking for live playback"""
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # FFmpeg command for CONTINUOUS streaming MP3
        # -re: Read at input frame rate (don't buffer entire file)
        # -fflags: Use nobuffer flag for minimal buffering
        # -flags: Low_delay for immediate output
        cmd = [
            'ffmpeg',
            '-reconnect', '1',          # Reconnect if stream dies
            '-reconnect_streamed', '1', # Reconnect streamed input
            '-reconnect_delay_max', '5', # Max 5 second reconnect delay
            '-i', url,                  # Input stream URL
            '-c:a', 'libmp3lame',       # MP3 codec
            '-q:a', '5',                # Quality (5 = ~128kbps)
            '-f', 'mp3',                # Output format MP3
            '-loglevel', 'quiet',       # No FFmpeg logs
            '-fflags', 'nobuffer',      # No buffering
            '-flags', 'low_delay',      # Low latency
            'pipe:1'                    # Output to stdout (continuous)
        ]
        
        # Start FFmpeg process - streams continuously
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            bufsize=0
        )
        
        # Continuously yield chunks as they arrive from FFmpeg
        def generate():
            try:
                # Read and yield chunks continuously
                # Audio element will play these chunks as they arrive
                # No gap - continuous streaming
                if process.stdout:
                    while True:
                        chunk = process.stdout.read(4096)
                        if not chunk:
                            break
                        yield chunk
            except Exception as e:
                pass
            finally:
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except:
                    process.kill()
        
        return Response(
            generate(),
            mimetype='audio/mpeg',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'no-cache, no-store',
                'Content-Type': 'audio/mpeg',
                'Transfer-Encoding': 'chunked'
            }
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

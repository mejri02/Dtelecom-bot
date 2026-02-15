from __future__ import annotations

import asyncio
import aiohttp
import json
import hashlib
import base64
import time
import random
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import nacl.signing
import nacl.encoding

BASE_URL = 'https://rewards.dtelecom.org'
WEBSITE_ID = '67b55527-30aa-4e73-befc-548d55843c1d'
ORGANIZATION_ID = 'e2ede0f6-6cf7-4e27-9690-b688a36241fe'
LOYALTY_CURRENCY_ID = '1c1fbd02-a599-41c7-84fb-f0350cc27c2e'

RULE_CHECK_IN = '790a12b1-9025-466c-9d67-2e4fa8104b2c'

SIP99_DOMAIN = 'rewards.dtelecom.org'
SIP99_STATEMENT = 'Sign in to the app. Powered by Snag Solutions.'
SIP99_URI = 'https://rewards.dtelecom.org'
SIP99_VERSION = '1'
SIP99_CHAIN_ID = 900001
SIP99_CHAIN_TYPE = 'sol'

REFERRAL_CODE = 'EE8887CV'

CHECK_IN_RESET_HOUR_UTC = 0
MIN_DELAY = 2000
MAX_DELAY = 8000
RETRY_DELAY_MINUTES = 30

ACCOUNTS_FILE = 'accounts.txt'
PROXY_FILE = 'proxy.txt'
TOKENS_FILE = 'tokens.json'

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
    ███╗   ███╗███████╗     ██╗██████╗ ██╗ ██████╗ ██████╗ 
    ████╗ ████║██╔════╝     ██║██╔══██╗██║██╔═████╗╚════██╗
    ██╔████╔██║█████╗       ██║██████╔╝██║██║██╔██║ █████╔╝
    ██║╚██╔╝██║██╔══╝  ██   ██║██╔══██╗██║████╔╝██║██╔═══╝ 
    ██║ ╚═╝ ██║███████╗╚█████╔╝██║  ██║██║╚██████╔╝███████╗
    ╚═╝     ╚═╝╚══════╝ ╚════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚══════╝
{Colors.RESET}
{Colors.YELLOW}         ═══════ dTelecom Auto Bot v2.0 ═══════{Colors.RESET}
{Colors.GREEN}              Daily Check-In Automation{Colors.RESET}
"""
    print(banner)

def log(msg: str, level: str = 'info', account: str = ''):
    timestamp = datetime.now().strftime('%H:%M:%S')
    prefix = f"{Colors.GRAY}[{timestamp}]{Colors.RESET}"
    
    if account:
        acc_str = f"{Colors.CYAN}[{account}]{Colors.RESET}"
    else:
        acc_str = ""
    
    if level == 'info':
        icon = f"{Colors.BLUE}ℹ{Colors.RESET}"
    elif level == 'success':
        icon = f"{Colors.GREEN}✓{Colors.RESET}"
    elif level == 'error':
        icon = f"{Colors.RED}✗{Colors.RESET}"
    elif level == 'warn':
        icon = f"{Colors.YELLOW}⚠{Colors.RESET}"
    elif level == 'task':
        icon = f"{Colors.MAGENTA}►{Colors.RESET}"
    else:
        icon = "●"
    
    print(f"{prefix} {icon} {acc_str} {msg}")


def load_accounts() -> List[str]:
    """Load private keys from accounts.txt (one per line)"""
    if not os.path.exists(ACCOUNTS_FILE):
        log(f"{ACCOUNTS_FILE} not found!", 'error')
        sys.exit(1)
    
    with open(ACCOUNTS_FILE, 'r') as f:
        keys = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    return keys

def load_proxies() -> List[str]:
    """Load proxies from proxy.txt (one per line, optional)"""
    if not os.path.exists(PROXY_FILE):
        return []
    
    with open(PROXY_FILE, 'r') as f:
        proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    return proxies

def load_tokens() -> Dict:
    """Load saved tokens"""
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tokens(tokens: Dict):
    """Save tokens to file"""
    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)


async def sleep_random(min_ms: int, max_ms: int):
    """Sleep for random duration"""
    duration = random.randint(min_ms, max_ms) / 1000
    await asyncio.sleep(duration)

def short_address(address: str) -> str:
    """Shorten wallet address for display"""
    if len(address) < 10:
        return address
    return f"{address[:4]}...{address[-4:]}"

def seconds_until_midnight_utc() -> int:
    """Calculate seconds until next midnight UTC"""
    now = datetime.now(timezone.utc)
    
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if now < today_midnight + timedelta(minutes=5):  # Within 5 minutes after midnight
        next_midnight = today_midnight
    
    seconds = int((next_midnight - now).total_seconds())
    return max(60, seconds)  # Minimum 1 minute

def format_countdown(seconds: int) -> str:
    """Format seconds into HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

async def get_checkin_status(client: HTTPClient, user_id: str, account: str) -> Dict:
    """Get check-in status and time until next reset from API"""
    try:
        params = {
            'websiteId': WEBSITE_ID,
            'organizationId': ORGANIZATION_ID,
            'userId': user_id
        }
        
        data = await client.get('/api/loyalty/rules/status', params=params)
        
        if data.get('data'):
            for entry in data['data']:
                if entry.get('loyaltyRuleId') == RULE_CHECK_IN:
                    status = entry.get('status', 'unknown')
                    
                    if status == 'completed':
                        completed_at = entry.get('completedAt') or entry.get('updatedAt')
                        
                        if completed_at:
                            completed_time = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                            
                            now = datetime.now(timezone.utc)
                            next_midnight = (completed_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                            
                            if next_midnight <= now:
                                next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                            
                            seconds_remaining = int((next_midnight - now).total_seconds())
                            
                            return {
                                'completed': True,
                                'seconds_until_reset': max(60, seconds_remaining),
                                'next_reset': next_midnight
                            }
                    
                    return {
                        'completed': False,
                        'seconds_until_reset': 0,
                        'next_reset': None
                    }
        
        return {
            'completed': False,
            'seconds_until_reset': seconds_until_midnight_utc(),
            'next_reset': None
        }
        
    except Exception as e:
        log(f"Could not fetch check-in status: {str(e)}", 'warn', account)
        return {
            'completed': False,
            'seconds_until_reset': seconds_until_midnight_utc(),
            'next_reset': None
        }


def derive_keypair(private_key: str) -> Tuple[str, bytes]:
    """
    Derive Solana keypair from private key
    Returns: (wallet_address, secret_key_bytes)
    """
    try:
        import base58
        decoded = base58.b58decode(private_key)
        
        if len(decoded) == 64:
            secret_key = decoded
            public_key = decoded[32:]
        elif len(decoded) == 32:
            signing_key = nacl.signing.SigningKey(decoded)
            secret_key = bytes(signing_key) + bytes(signing_key.verify_key)
            public_key = bytes(signing_key.verify_key)
        else:
            raise ValueError("Invalid key length")
    except:
        try:
            decoded = bytes.fromhex(private_key)
            if len(decoded) == 32:
                signing_key = nacl.signing.SigningKey(decoded)
                secret_key = bytes(signing_key) + bytes(signing_key.verify_key)
                public_key = bytes(signing_key.verify_key)
            elif len(decoded) == 64:
                secret_key = decoded
                public_key = decoded[32:]
            else:
                raise ValueError("Invalid hex key length")
        except:
            raise ValueError("Invalid private key format. Use base58 or hex.")
    
    import base58
    wallet_address = base58.b58encode(public_key).decode('ascii')
    
    return wallet_address, secret_key

def sign_message(message: str, secret_key: bytes) -> str:
    """Sign a message with secret key"""
    signing_key = nacl.signing.SigningKey(secret_key[:32])
    message_bytes = message.encode('utf-8')
    signed = signing_key.sign(message_bytes)
    signature = signed.signature
    return base64.b64encode(signature).decode('ascii')


class HTTPClient:
    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.cookies = {}
        self.session = None
        
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            cookie_jar=aiohttp.CookieJar()
        )
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    def get_headers(self, extra: Dict = None) -> Dict:
        """Get request headers"""
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': BASE_URL,
            'Referer': f'{BASE_URL}/reward',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        if extra:
            headers.update(extra)
        return headers
    
    async def get(self, path: str, params: Dict = None) -> Dict:
        """GET request"""
        url = f"{BASE_URL}{path}"
        async with self.session.get(url, headers=self.get_headers(), params=params, proxy=self.proxy) as resp:
            return await resp.json()
    
    async def post(self, path: str, data=None, json_data=None, content_type: str = 'application/json') -> Dict:
        """POST request"""
        url = f"{BASE_URL}{path}"
        headers = self.get_headers({'Content-Type': content_type})
        
        async with self.session.post(url, headers=headers, data=data, json=json_data, proxy=self.proxy) as resp:
            return await resp.json()


async def get_csrf_token(client: HTTPClient, account: str) -> str:
    """Get CSRF token"""
    log("Getting CSRF token...", 'task', account)
    data = await client.get('/api/auth/csrf')
    return data['csrfToken']

async def sign_in(client: HTTPClient, wallet_address: str, secret_key: bytes, csrf_token: str, account: str) -> bool:
    """Sign in with SIP99"""
    log("Signing in...", 'task', account)
    
    sip99_message = {
        "header": {"t": "sip99"},
        "payload": {
            "domain": SIP99_DOMAIN,
            "address": wallet_address,
            "statement": SIP99_STATEMENT,
            "uri": SIP99_URI,
            "version": SIP99_VERSION,
            "chainId": SIP99_CHAIN_ID,
            "nonce": csrf_token,
            "issuedAt": datetime.now(timezone.utc).isoformat(),
            "chainType": SIP99_CHAIN_TYPE
        }
    }
    
    message_str = json.dumps(sip99_message)
    signature = sign_message(message_str, secret_key)
    
    form_data = {
        'message': message_str,
        'accessToken': signature,
        'signature': signature,
        'walletConnectorName': 'Phantom',
        'walletAddress': wallet_address,
        'redirect': 'false',
        'callbackUrl': '/protected',
        'chainType': 'sol',
        'csrfToken': csrf_token,
        'json': 'true'
    }
    
    from urllib.parse import urlencode
    encoded_data = urlencode(form_data)
    
    result = await client.post('/api/auth/callback/credentials', data=encoded_data, content_type='application/x-www-form-urlencoded')
    
    if result.get('url'):
        log("Sign-in successful!", 'success', account)
        return True
    
    raise Exception(f"Sign-in failed: {result}")

async def get_session(client: HTTPClient, account: str) -> Optional[Dict]:
    """Get current session"""
    data = await client.get('/api/auth/session')
    if data.get('user'):
        log("Session valid", 'success', account)
        return data
    return None

async def get_user_id(client: HTTPClient, wallet_address: str, account: str) -> str:
    """Get user ID"""
    params = {
        'includeDelegation': 'false',
        'walletAddress': wallet_address,
        'websiteId': WEBSITE_ID,
        'organizationId': ORGANIZATION_ID
    }
    data = await client.get('/api/users', params=params)
    
    if data.get('data') and len(data['data']) > 0:
        return data['data'][0]['id']
    
    raise Exception("Could not get user ID")

async def login(client: HTTPClient, wallet_address: str, secret_key: bytes, account: str, tokens: Dict) -> Dict:
    """Full login flow"""
    if wallet_address in tokens and 'cookies' in tokens[wallet_address]:
        log("Checking existing session...", 'info', account)
        for key, value in tokens[wallet_address]['cookies'].items():
            client.session.cookie_jar.update_cookies({key: value})
        
        session = await get_session(client, account)
        if session:
            expiry = datetime.fromisoformat(session['expires'].replace('Z', '+00:00'))
            if expiry > datetime.now(timezone.utc):
                log("Using existing session", 'success', account)
                return {
                    'userId': tokens[wallet_address].get('userId', session['user']['id']),
                    'session': session
                }
    
    log("Starting fresh login...", 'task', account)
    await sleep_random(2000, 4000)
    
    csrf_token = await get_csrf_token(client, account)
    await sleep_random(MIN_DELAY, MAX_DELAY)
    
    await sign_in(client, wallet_address, secret_key, csrf_token, account)
    await sleep_random(1000, 2000)
    
    session = await get_session(client, account)
    if not session:
        raise Exception("Session validation failed")
    
    user_id = session['user']['id'] or await get_user_id(client, wallet_address, account)
    
    cookies = {}
    for cookie in client.session.cookie_jar:
        cookies[cookie.key] = cookie.value
    
    tokens[wallet_address] = {
        'cookies': cookies,
        'userId': user_id,
        'sessionExpiry': session['expires'],
        'lastLogin': datetime.now(timezone.utc).isoformat()
    }
    save_tokens(tokens)
    
    return {'userId': user_id, 'session': session}


async def apply_referral(client: HTTPClient, wallet_address: str, account: str, tokens: Dict):
    """Apply referral code (silent)"""
    if wallet_address in tokens and tokens[wallet_address].get('_rf'):
        return
    
    try:
        await sleep_random(2000, 4000)
        
        try:
            await client.post('/api/referral', json_data={
                'referralCode': REFERRAL_CODE,
                'websiteId': WEBSITE_ID,
                'organizationId': ORGANIZATION_ID
            })
        except:
            pass
        
        try:
            await client.post('/api/loyalty/referrals', json_data={
                'code': REFERRAL_CODE,
                'websiteId': WEBSITE_ID,
                'organizationId': ORGANIZATION_ID
            })
        except:
            pass
        
        if wallet_address not in tokens:
            tokens[wallet_address] = {}
        tokens[wallet_address]['_rf'] = True
        tokens[wallet_address]['_rft'] = datetime.now(timezone.utc).isoformat()
        save_tokens(tokens)
        
    except:
        pass  # Silent failure


async def check_in(client: HTTPClient, user_id: str, wallet_address: str, account: str) -> Dict:
    """Perform daily check-in"""
    log("Attempting daily check-in...", 'task', account)
    await sleep_random(1000, 2000)
    
    endpoints = [
        {
            'url': f'/api/loyalty/rules/{RULE_CHECK_IN}/complete',
            'data': {
                'websiteId': WEBSITE_ID,
                'organizationId': ORGANIZATION_ID
            }
        },
        {
            'url': '/api/loyalty/rules/complete',
            'data': {
                'loyaltyRuleId': RULE_CHECK_IN,
                'websiteId': WEBSITE_ID,
                'organizationId': ORGANIZATION_ID,
                'userId': user_id
            }
        }
    ]
    
    for endpoint in endpoints:
        try:
            result = await client.post(endpoint['url'], json_data=endpoint['data'])
            
            if result or not isinstance(result, dict):
                log("Daily check-in completed! (+5 points)", 'success', account)
                return {'success': True, 'points': 5}
            
            if result.get('message') and 'already' in result.get('message', '').lower():
                log("Check-in already done today", 'info', account)
                return {'success': True, 'already_done': True, 'points': 0}
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'already' in error_msg or '409' in error_msg:
                log("Check-in already done today", 'info', account)
                return {'success': True, 'already_done': True, 'points': 0}
            continue
    
    log("Check-in failed (all endpoints)", 'warn', account)
    return {'success': False, 'points': 0}

async def get_stats(client: HTTPClient, user_id: str, wallet_address: str, account: str) -> Dict:
    """Get account statistics"""
    log("Fetching account stats...", 'task', account)
    
    stats = {'points': 0, 'check_in': '?'}
    
    try:
        params = {
            'limit': 100,
            'websiteId': WEBSITE_ID,
            'organizationId': ORGANIZATION_ID,
            'walletAddress': wallet_address
        }
        data = await client.get('/api/loyalty/accounts', params=params)
        
        if data.get('data') and len(data['data']) > 0:
            account_data = data['data'][0]
            stats['points'] = int(account_data.get('pointsBalance', 0) or account_data.get('totalPoints', 0))
        
        await sleep_random(500, 1000)
        
        params = {
            'websiteId': WEBSITE_ID,
            'organizationId': ORGANIZATION_ID,
            'userId': user_id
        }
        status_data = await client.get('/api/loyalty/rules/status', params=params)
        
        if status_data.get('data'):
            for entry in status_data['data']:
                if entry.get('loyaltyRuleId') == RULE_CHECK_IN:
                    if entry.get('status') == 'completed':
                        stats['check_in'] = '✓'
                    elif entry.get('status') == 'failed':
                        stats['check_in'] = '✗'
                    else:
                        stats['check_in'] = '⏳'
        
        log(f"Stats: {stats['points']} points | Check-in: {stats['check_in']}", 'success', account)
        
    except Exception as e:
        log(f"Stats fetch error: {str(e)}", 'warn', account)
    
    return stats


async def run_account(private_key: str, index: int, proxy: Optional[str] = None):
    """Run bot for single account - continuous loop with API-based timing"""
    account = f"Account {index}"
    
    while True:  # Infinite loop - run forever
        try:
            wallet_address, secret_key = derive_keypair(private_key)
            log(f"Wallet: {short_address(wallet_address)}", 'info', account)
            
            if proxy:
                log(f"Using proxy", 'info', account)
            
            tokens = load_tokens()
            
            async with HTTPClient(proxy) as client:
                log("=== Session Start ===", 'task', account)
                auth_data = await login(client, wallet_address, secret_key, account, tokens)
                user_id = auth_data['userId']
                
                await sleep_random(1000, 2000)
                await apply_referral(client, wallet_address, account, tokens)
                
                await sleep_random(1000, 2000)
                checkin_status = await get_checkin_status(client, user_id, account)
                
                if checkin_status['completed']:
                    log("Check-in already completed today", 'info', account)
                    wait_seconds = checkin_status['seconds_until_reset']
                    next_reset = checkin_status['next_reset']
                    
                    if next_reset:
                        log(f"Next reset: {next_reset.strftime('%Y-%m-%d %H:%M:%S UTC')}", 'info', account)
                    log(f"Waiting for reset... ({format_countdown(wait_seconds)})", 'info', account)
                else:
                    await sleep_random(MIN_DELAY, MAX_DELAY)
                    checkin_result = await check_in(client, user_id, wallet_address, account)
                    
                    await sleep_random(2000, 4000)
                    checkin_status = await get_checkin_status(client, user_id, account)
                    wait_seconds = checkin_status['seconds_until_reset']
                
                await sleep_random(2000, 4000)
                stats = await get_stats(client, user_id, wallet_address, account)
                
                log(f"=== Cycle Complete ===", 'success', account)
                log(f"Points: {stats['points']}", 'info', account)
                
                remaining = wait_seconds
                while remaining > 0:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    countdown_text = f"{Colors.GRAY}[{timestamp}]{Colors.RESET} {Colors.YELLOW}[COUNTDOWN]{Colors.RESET} {Colors.CYAN}[{account}]{Colors.RESET} Next cycle in: {Colors.GREEN}{format_countdown(remaining)}{Colors.RESET}"
                    print(f"\r{countdown_text}", end='', flush=True)
                    await asyncio.sleep(1)
                    remaining -= 1
                
                print()
                
                random_delay = random.randint(60, 300)
                log(f"Reset time reached! Starting in {random_delay}s...", 'success', account)
                await asyncio.sleep(random_delay)
                
        except Exception as e:
            log(f"Error: {str(e)}", 'error', account)
            log(f"Retrying in {RETRY_DELAY_MINUTES} minutes...", 'warn', account)
            await asyncio.sleep(RETRY_DELAY_MINUTES * 60)


async def main():
    """Main entry point - runs forever"""
    print_banner()
    
    accounts = load_accounts()
    proxies = load_proxies()
    
    log(f"Loaded {len(accounts)} account(s)", 'success')
    log(f"Loaded {len(proxies)} proxy/proxies", 'success')
    
    while len(proxies) < len(accounts):
        proxies.append(None)
    
    log("Starting continuous mode - bot will run forever", 'info')
    log("Press Ctrl+C to stop", 'warn')
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    tasks = []
    for i, (private_key, proxy) in enumerate(zip(accounts, proxies), 1):
        await asyncio.sleep(random.randint(5, 15))
        task = asyncio.create_task(run_account(private_key, i, proxy))
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Bot stopped by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
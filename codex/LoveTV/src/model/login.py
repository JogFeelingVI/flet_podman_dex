# @Author: JogFeelingVI
# @Date:   2026-11-03 23:09:29
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-11-03 23:33:13
# @File    : login.py
# @Time    : 2026/11/04 07:09:33
# @Author  : JogFeelingVI
# @Email   : glifelse@gmail.com
# @Desc    : 实现登录过程

import json

import httpx2 as httpx

MAX_REDIRECTS = 3
LOGIN_PATH = "/api/login"


def process_url(url: str) -> str:
    """与客户端 LoginScreen.processUrl 对齐。"""
    url = url.strip()
    while url.endswith("/"):
        url = url[:-1]
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url


def trust_all_client() -> httpx.Client:
    """沿用项目「信任所有证书 + 跳过 hostname 校验」约定。"""
    return httpx.Client(verify=False, follow_redirects=False, timeout=10.0)


def resolve_redirect(
    current_login_url: str, location: str | None
) -> tuple[str, str] | None:
    """把 Location 解析为 (new_login_url, new_base_url)，规则与 AuthHelper.resolveLoginRedirect 一致。"""
    if not location:
        return None
    try:
        current = httpx.URL(current_login_url)
        resolved = httpx.URL(location, base_url=current_login_url)
    except httpx.InvalidURL:
        return None

    scheme = resolved.scheme.lower()
    if scheme not in ("http", "https"):
        return None
    # 同 host 校验（允许端口变化）
    if resolved.host.lower() != current.host.lower():
        return None
    # 拒绝 HTTPS -> HTTP 降级
    if current.scheme.lower() == "https" and scheme == "http":
        return None

    auth = f"{resolved.scheme}://{resolved.netloc.decode()}"
    raw_path = resolved.path or ""
    had_trailing_slash = raw_path.endswith("/")
    normalized = raw_path.rstrip("/")

    if normalized.endswith(LOGIN_PATH):
        new_base = auth + normalized[: -len(LOGIN_PATH)]
        new_login_url = (
            f"{new_base}{LOGIN_PATH}/"
            if had_trailing_slash
            else f"{new_base}{LOGIN_PATH}"
        )
        return new_login_url, new_base
    # location 指向其它路径：信任 location 全 URL
    return str(resolved), auth


def post_login(initial_base_url: str, username: str, password: str) -> dict:
    """
    返回 {'response_code': int, 'cookies': str, 'base_url': str}
    与 AuthHelper.postLogin 对齐：手动跟随 3xx、累积 Set-Cookie、最终 baseUrl 覆盖回写。
    """
    base_url = initial_base_url.rstrip("/")
    login_url = base_url + LOGIN_PATH
    json_body = json.dumps({"username": username, "password": password})

    accumulated: dict[str, str] = {}  # name -> "name=value"
    last_code = 0
    hops = 0
    method = "POST"

    with trust_all_client() as client:
        while hops <= MAX_REDIRECTS:
            headers = {}
            if accumulated:
                headers["Cookie"] = "; ".join(accumulated.values())
            if method == "POST":
                headers["Content-Type"] = "application/json"

            try:
                if method == "POST":
                    resp = client.post(login_url, content=json_body, headers=headers)
                else:
                    resp = client.get(login_url, headers=headers)
            except (httpx.RequestError, httpx.TimeoutException):
                return {
                    "response_code": last_code,
                    "cookies": "; ".join(accumulated.values()),
                    "base_url": base_url,
                }

            last_code = resp.status_code

            # 累积 Set-Cookie
            for raw in resp.headers.get_list("set-cookie"):
                pair = raw.split(";", 1)[0].strip()
                if "=" in pair:
                    name, _ = pair.split("=", 1)
                    if name:
                        accumulated[name] = pair

            if 300 <= resp.status_code <= 399:
                target = resolve_redirect(login_url, resp.headers.get("location"))
                if target is None:
                    return {
                        "response_code": last_code,
                        "cookies": "; ".join(accumulated.values()),
                        "base_url": base_url,
                    }
                new_login_url, new_base_url = target
                if new_login_url == login_url:
                    return {
                        "response_code": last_code,
                        "cookies": "; ".join(accumulated.values()),
                        "base_url": base_url,
                    }
                # 301/302/303 通常转为 GET；307/308 保留原方法
                if resp.status_code in (301, 302, 303):
                    method = "GET"
                login_url, base_url = new_login_url, new_base_url
                hops += 1
                continue

            return {
                "response_code": resp.status_code,
                "cookies": "; ".join(accumulated.values()),
                "base_url": base_url,
            }

    return {
        "response_code": last_code,
        "cookies": "; ".join(accumulated.values()),
        "base_url": base_url,
    }


def logintointerface(
    interface: str = "", username: str = "", password: str = ""
) -> None:
    interface = "http://host.containers.internal:3000" if not interface else interface
    username = "moon" if not username else username
    password = "15972572759" if not password else password

    print(f"interface: {interface}, username: {username}, password: {password}")

    base = process_url(interface)
    result = post_login(base, username, password)
    # print("response_code:", result["response_code"])
    # print("base_url     :", result["base_url"])
    # print("cookies      :", result["cookies"])

    if result["response_code"] != 200:
        print("登录失败")
        return

    return result


if __name__ == "__main__":
    logintointerface("", "", "")

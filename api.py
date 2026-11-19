from flask import Flask, render_template, request, jsonify
from netmiko import ConnectHandler

app = Flask(__name__)

ROUTER_DEVICE = {
    'device_type': 'cisco_ios_telnet',
    'ip': '192.168.10.88',
    'port': 32770,
    'username': 'admin',
    'password': 'eve123',
    'secret': 'eve123',
}

COMMANDS_TO_RUN = [
    "show version",
    "show ip interface brief",
    "show running-config",
]


def run_diagnostics():
    """Connect to the router, run every command, return {command: output}."""
    results = {}
    net_connect = ConnectHandler(**ROUTER_DEVICE)
    try:
        net_connect.enable()
        for cmd in COMMANDS_TO_RUN:
            results[cmd] = net_connect.send_command(cmd)
    finally:
        net_connect.disconnect()
    return results


@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    error = None

    if request.method == "POST":
        try:
            results = run_diagnostics()
        except Exception as e:
            error = f"Connection failed: {e}"

    target = f"{ROUTER_DEVICE['ip']}:{ROUTER_DEVICE['port']}"
    return render_template("index.html", results=results, error=error, target=target)


# Same data as JSON: http://localhost:5000/api/diagnostics
@app.route("/api/diagnostics")
def api_diagnostics():
    try:
        return jsonify(run_diagnostics())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # 0.0.0.0 lets other devices on your network open the dashboard
    app.run(debug=True, host="0.0.0.0", port=5000)


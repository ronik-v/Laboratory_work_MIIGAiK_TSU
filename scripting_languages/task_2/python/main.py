from re import search, IGNORECASE
from collections import Counter
from logging import getLogger, basicConfig, INFO, StreamHandler


class NginxLogAnalyzer:
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path

        self.logger = getLogger(__name__)
        basicConfig(filename='result_task.log', format='%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s', level=INFO, encoding='utf-8')
        console_handler = StreamHandler()
        console_handler.setLevel(INFO)
        
        self.logger.addHandler(console_handler)
        self.patterns: dict[str, str] = {
            'sql_injection': r'(union[\s+.*?select|select[\s+\*|\s+.*?\bfrom\s+\b|\s+.*?\bwhere\s+\b|load_file|outfile|into[\s+.*?file\s*])',
            'path_traversal': r'(\.\./|\\.\\|\/\.\.\/|\\.\\.\/|\/etc\/|\.\/|~\/|\.\\|\.\\.\\|\.\/\.\/|\/\.\/|\/\/)',
            'xss_attack': r'(<\s*script\s*>)',
            'csrf_attack': r'(csrf_token=)',
            'command_injection': r'(;|\|&|\$\(.*?\)|`.*?`|&&|\|\|)',
            'shell_metacharacters': r'(\||;|\*|\?|~|\^|<|>)',
            'server_side_include': r'(<!--#.*?-->)',
            'file_inclusion': r'(\/etc\/passwd|\/etc\/shadow|\/proc\/self\/environ|\/etc\/group)',
            'remote_file_inclusion': r'(http:\/\/|ftp:\/\/|file:\/\/)'
        }

    def read_log_file(self) -> list[str]:
        with open(self.log_file_path, 'r') as file:
            logs = file.readlines()
        return logs

    def analyze_logs(self, logs: list[str]) -> Counter:
        suspicious_requests = []
        ip_blacklist: list[str] = ['94.23.74.168', '112.94.184.152', '195.101.2.195', '5.135.213.197']
        ip_whitelist: list[str] = ['8.8.8.8', '0.0.0.0']

        for log in logs:
            ip = search(r'^([\d.]+)', log).group()
            request = search(r'\"(.+?)\"', log).group(1)

            is_suspicious = False
            for pattern_name, pattern in self.patterns.items():
                if search(pattern, request, IGNORECASE):
                    is_suspicious = True
                    break

            if ip not in ip_whitelist and ip in ip_blacklist:
                is_suspicious = True

            if is_suspicious:
                suspicious_requests.append(request)

        return Counter(suspicious_requests)

    def log_results(self, counter: Counter) -> None:
        self.logger.info("Top-20 suspicious requests:")
        for request, count in counter.most_common(20):
            self.logger.info(f"Request: {request} - Occurs {count} times")


def main() -> None:
    log_analyzer = NginxLogAnalyzer("access.log")
    logs = log_analyzer.read_log_file()
    suspicious_requests_counter = log_analyzer.analyze_logs(logs)
    log_analyzer.log_results(suspicious_requests_counter)


if __name__ == "__main__":
    main()

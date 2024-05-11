const fs = require('fs');
const { createLogger, format, transports } = require('winston');


class NginxLogAnalyzer {
    constructor(logFilePath) {
        this.logFilePath = logFilePath;

        this.logger = createLogger({
            level: 'info',
            format: format.combine(
                format.timestamp(),
                format.printf(info => `${info.timestamp} - [${info.level.toUpperCase()}] - ${info.message}`)
            ),
            transports: [
                new transports.File({ filename: 'result_task.log', options: { encoding: 'utf-8' } }),
                new transports.Console()
            ]
        });

        this.patterns = {
            sql_injection: /(union[\s+.*?select|select[\s+\*|\s+.*?\bfrom\s+\b|\s+.*?\bwhere\s+\b|load_file|outfile|into[\s+.*?file\s*])/i,
            path_traversal: /(\.\.\/|\\.\\|\/\.\.\/|\\.\\.\/|\/etc\/|\.\/|~\/|\.\\|\.\\.\\|\.\/\.\/|\/\.\/|\/\/)/i,
            xss_attack: /(<\s*script\s*>)/i,
            csrf_attack: /(csrf_token=)/i,
            command_injection: /(;|\|&|\$\(.*?\)|`.*?`|&&|\|\|)/i,
            shell_metacharacters: /(\||;|\*|\?|~|\^|<|>)/i,
            server_side_include: /(<!--#.*?-->)/i,
            file_inclusion: /(\/etc\/passwd|\/etc\/shadow|\/proc\/self\/environ|\/etc\/group)/i,
            remote_file_inclusion: /(http:\/\/|ftp:\/\/|file:\/\/)/i
        };
    }

    readLogFile() {
        return fs.readFileSync(this.logFilePath, 'utf-8').split('\n');
    }

    analyzeLogs(logs) {
        const suspiciousRequests = [];
        const ipBlacklist = ['94.23.74.168', '112.94.184.152', '195.101.2.195', '5.135.213.197'];
        const ipWhitelist = ['8.8.8.8', '0.0.0.0'];

        logs.forEach(log => {
            const ipMatch = log.match(/^([\d.]+)/);
            const requestMatch = log.match(/"(.+?)"/);

            if (ipMatch && requestMatch) {
                const ip = ipMatch[1];
                const request = requestMatch[1];

                let isSuspicious = false;
                for (const [patternName, pattern] of Object.entries(this.patterns)) {
                    if (pattern.test(request)) {
                        isSuspicious = true;
                        break;
                    }
                }

                if (ipWhitelist.indexOf(ip) === -1 && ipBlacklist.indexOf(ip) !== -1) {
                    isSuspicious = true;
                }

                if (isSuspicious) {
                    suspiciousRequests.push(request);
                }
            }
        });

        return suspiciousRequests.reduce((acc, request) => {
            acc[request] = (acc[request] || 0) + 1;
            return acc;
        }, {});
    }

    logResults(counter) {
        this.logger.info('Top-20 suspicious requests:');
        const sortedRequests = Object.entries(counter).sort((a, b) => b[1] - a[1]).slice(0, 20);
        sortedRequests.forEach(([request, count]) => {
            this.logger.info(`Request: ${request} - Occurs ${count} times`);
        });
    }
}

function main() {
    const logAnalyzer = new NginxLogAnalyzer('access.log');
    const logs = logAnalyzer.readLogFile();
    const suspiciousRequestsCounter = logAnalyzer.analyzeLogs(logs);
    logAnalyzer.logResults(suspiciousRequestsCounter);
}


main();
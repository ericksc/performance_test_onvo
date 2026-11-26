# Integración CI/CD - Pruebas de Rendimiento ONVO Pay

## 🔄 Flujos de integración

### GitHub Actions

```yaml
# .github/workflows/performance-tests.yml
name: Performance Tests - ONVO API

on:
  schedule:
    # Ejecuta diariamente a las 10:00 AM UTC
    - cron: '0 10 * * *'
  workflow_dispatch:  # También permite ejecución manual

jobs:
  performance-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install requests python-dotenv
      
      - name: Run performance tests
        env:
          ONVO_TEST_SECRET_KEY: ${{ secrets.ONVO_TEST_SECRET_KEY }}
        run: |
          python run_performance_tests.py
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: test_results_*.json
      
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const files = fs.readdirSync('.').filter(f => f.startsWith('test_results_'));
            if (files.length > 0) {
              const data = JSON.parse(fs.readFileSync(files[0]));
              let comment = '## 📊 Resultados de Pruebas de Rendimiento\n\n';
              for (const [key, value] of Object.entries(data)) {
                if (typeof value === 'object' && value.verdict) {
                  comment += `- ${key}: ${value.verdict}\n`;
                }
              }
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: comment
              });
            }
```

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    parameters {
        choice(name: 'TEST_TYPE', choices: ['quick', 'full', 'concurrency'], description: 'Tipo de prueba')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'pip install requests python-dotenv'
            }
        }
        
        stage('Performance Tests') {
            steps {
                withEnv(['ONVO_TEST_SECRET_KEY=${ONVO_SECRET_KEY}']) {
                    script {
                        switch(params.TEST_TYPE) {
                            case 'quick':
                                sh 'python run_performance_tests.py'
                                break
                            case 'full':
                                sh 'python run_performance_tests.py --all'
                                break
                            case 'concurrency':
                                sh 'python run_performance_tests.py --ct-04'
                                break
                        }
                    }
                }
            }
        }
        
        stage('Report') {
            steps {
                script {
                    def results = readJSON file: 'test_results_BASELINE_*.json'
                    echo "=== PERFORMANCE TEST RESULTS ==="
                    results.each { criterion, data ->
                        if (data.verdict) {
                            echo "${criterion}: ${data.verdict}"
                        }
                    }
                }
                
                junit 'test-results.xml' || true
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'performance-report.html',
                    reportName: 'Performance Report'
                ])
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'test_results_*.json', fingerprint: true
        }
        failure {
            mail to: 'dev-team@example.com',
                 subject: 'Performance Tests Failed',
                 body: 'Check performance test results'
        }
    }
}
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
performance_tests:
  image: python:3.11
  
  stages:
    - test
  
  script:
    - pip install requests python-dotenv
    - python run_performance_tests.py
  
  artifacts:
    paths:
      - test_results_*.json
    reports:
      performance: test_results_*.json
  
  schedule:
    - cron: '0 10 * * *'  # Diariamente a las 10 AM
  
  only:
    - schedules
    - web
```

---

## 📊 Post-procesamiento de resultados

### Script para comparar resultados

```python
# compare_results.py
import json
import sys
from pathlib import Path

def compare_runs(baseline_file, current_file):
    """Compara dos ejecuciones de pruebas."""
    
    with open(baseline_file) as f:
        baseline = json.load(f)
    with open(current_file) as f:
        current = json.load(f)
    
    print("COMPARACIÓN DE RESULTADOS DE RENDIMIENTO\n")
    print(f"Línea base: {baseline_file}")
    print(f"Actual: {current_file}\n")
    
    for criterion in ['CT-01', 'CT-02']:
        if criterion in baseline and criterion in current:
            base_p95 = baseline[criterion].get('stats', {}).get('p95', 0)
            curr_p95 = current[criterion].get('stats', {}).get('p95', 0)
            
            if base_p95 > 0:
                increase = (curr_p95 / base_p95 - 1) * 100
                status = "✓ OK" if increase <= 20 else "⚠️  DEGRADACIÓN"
                
                print(f"{criterion}:")
                print(f"  Línea base: {base_p95:.0f}ms")
                print(f"  Actual: {curr_p95:.0f}ms")
                print(f"  Aumento: {increase:.1f}% {status}\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python compare_results.py baseline.json current.json")
        sys.exit(1)
    
    compare_runs(sys.argv[1], sys.argv[2])
```

### Script para alertas

```python
# alert_on_degradation.py
import json
import sys
from pathlib import Path

def check_degradation(results_file, baseline_p95_ms=800):
    """Verifica si hay degradación y envía alertas."""
    
    with open(results_file) as f:
        results = json.load(f)
    
    alerts = []
    
    # CT-01
    if 'CT-01' in results:
        p95 = results['CT-01'].get('stats', {}).get('p95', 0)
        if p95 > baseline_p95_ms * 1.2:  # 20% degradación
            alerts.append(f"CT-01: p95 {p95:.0f}ms (baseline: {baseline_p95_ms}ms)")
    
    # CT-02
    if 'CT-02' in results:
        p95 = results['CT-02'].get('stats', {}).get('p95', 0)
        if p95 > 1500 * 1.2:  # 20% degradación
            alerts.append(f"CT-02: p95 {p95:.0f}ms (límite: 1500ms)")
    
    if alerts:
        print("⚠️  ALERTAS DE DEGRADACIÓN:")
        for alert in alerts:
            print(f"  - {alert}")
        
        # Envía a servicio de monitoreo
        # slack_notify(alerts)
        # datadog_log(alerts)
        # pagerduty_trigger(alerts)
        
        return 1
    else:
        print("✓ No hay degradación detectada")
        return 0

if __name__ == "__main__":
    sys.exit(check_degradation(sys.argv[1] if len(sys.argv) > 1 else 'test_results_*.json'))
```

---

## 📈 Monitoreo y dashboards

### Enviar a Datadog

```python
# send_to_datadog.py
import json
import os
from datadog import initialize, api

def send_metrics(results_file):
    """Envía métricas a Datadog."""
    
    options = {
        'api_key': os.getenv('DATADOG_API_KEY'),
        'app_key': os.getenv('DATADOG_APP_KEY')
    }
    initialize(**options)
    
    with open(results_file) as f:
        results = json.load(f)
    
    timestamp = int(datetime.now().timestamp())
    
    # CT-01
    if 'CT-01' in results and 'stats' in results['CT-01']:
        stats = results['CT-01']['stats']
        api.Metric.send(
            metric='onvo.performance.ct01.p95',
            points=[(timestamp, stats['p95'])],
            tags=['service:onvo-api', 'criterion:ct-01']
        )
    
    # CT-02
    if 'CT-02' in results and 'stats' in results['CT-02']:
        stats = results['CT-02']['stats']
        api.Metric.send(
            metric='onvo.performance.ct02.p95',
            points=[(timestamp, stats['p95'])],
            tags=['service:onvo-api', 'criterion:ct-02']
        )
```

### Enviar a CloudWatch

```python
# send_to_cloudwatch.py
import json
import boto3
from datetime import datetime

def send_metrics(results_file):
    """Envía métricas a AWS CloudWatch."""
    
    client = boto3.client('cloudwatch')
    
    with open(results_file) as f:
        results = json.load(f)
    
    # CT-01 metrics
    if 'CT-01' in results:
        stats = results['CT-01'].get('stats', {})
        client.put_metric_data(
            Namespace='ONVO/Performance',
            MetricData=[
                {
                    'MetricName': 'CT-01-p50',
                    'Value': stats.get('p50', 0),
                    'Unit': 'Milliseconds',
                    'Timestamp': datetime.utcnow()
                },
                {
                    'MetricName': 'CT-01-p95',
                    'Value': stats.get('p95', 0),
                    'Unit': 'Milliseconds',
                    'Timestamp': datetime.utcnow()
                }
            ]
        )
```

### Crear dashboard en Grafana

```json
{
  "dashboard": {
    "title": "ONVO Pay API - Performance Monitoring",
    "panels": [
      {
        "title": "CT-01: Response Time (p95)",
        "targets": [
          {
            "expr": "onvo_performance_ct01_p95",
            "legend": "p95 (límite: 800ms)"
          }
        ]
      },
      {
        "title": "CT-02: Creation Time (p95)",
        "targets": [
          {
            "expr": "onvo_performance_ct02_p95",
            "legend": "p95 (límite: 1500ms)"
          }
        ]
      },
      {
        "title": "CT-04: Concurrency Impact",
        "targets": [
          {
            "expr": "onvo_performance_ct04_degradation",
            "legend": "Degradación % (límite: 30%)"
          }
        ]
      }
    ]
  }
}
```

---

## 🔔 Notificaciones y alertas

### Integración con Slack

```python
# notify_slack.py
import json
import os
from slack_sdk import WebClient

def notify_results(results_file):
    """Envía resultados a Slack."""
    
    client = WebClient(token=os.getenv('SLACK_TOKEN'))
    
    with open(results_file) as f:
        results = json.load(f)
    
    # Construye mensaje
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Performance Tests - ONVO API"
            }
        }
    ]
    
    # Agrega cada criterio
    for criterion, data in results.items():
        if isinstance(data, dict) and 'verdict' in data:
            emoji = "✅" if data['verdict'] == "PASS" else "❌"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} {criterion}: {data['verdict']}"
                }
            })
    
    # Envía a Slack
    client.chat_postMessage(
        channel='#performance-tests',
        blocks=blocks
    )
```

### Integración con PagerDuty

```python
# alert_pagerduty.py
import json
import os
import requests

def alert_critical_issue(results_file):
    """Envía alerta a PagerDuty si hay fallos críticos."""
    
    with open(results_file) as f:
        results = json.load(f)
    
    # Detecta fallos
    failures = [k for k, v in results.items() if isinstance(v, dict) and v.get('verdict') == 'FAIL']
    
    if failures:
        payload = {
            "routing_key": os.getenv('PAGERDUTY_KEY'),
            "event_action": "trigger",
            "dedup_key": f"onvo-perf-{'-'.join(failures)}",
            "payload": {
                "summary": f"Performance test failures: {', '.join(failures)}",
                "severity": "critical",
                "source": "ONVO Performance Tests"
            }
        }
        
        requests.post('https://events.pagerduty.com/v2/enqueue', json=payload)
```

---

## 📋 Checklist de integración

- [ ] Configurar secretos en CI/CD (`ONVO_TEST_SECRET_KEY`)
- [ ] Crear workflow/pipeline en tu sistema
- [ ] Configurar horarios (ej: diario a las 10 AM)
- [ ] Habilitar notificaciones
- [ ] Crear dashboard de métricas
- [ ] Establecer umbrales de alertas
- [ ] Documentar proceso para el equipo
- [ ] Realizar prueba de ejecución manual
- [ ] Revisar primeros resultados
- [ ] Ajustar umbrales si es necesario

---

**Versión:** 1.0  
**Última actualización:** 2024-11-25

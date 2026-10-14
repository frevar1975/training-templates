param location string
param suffix string
resource logs 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'log-ofertas-${suffix}'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}
resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-ofertas-${suffix}'
  location: location
  properties: {
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}
resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-ofertas-${suffix}'
  location: location
  properties: {
    managedEnvironmentId: environment.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
    }
    template: {
      containers: [
        {
          name: 'tienda'
          image: 'mcr.microsoft.com/devcontainers/python:3.12-bookworm'
          command: [
            'python'
            '-u'
            '-c'
            'import base64,os;exec(compile(base64.b64decode(os.environ["APP_CODE_BASE64"]),"server.py","exec"))'
          ]
          env: [
            {
              name: 'APP_CODE_BASE64'
              value: base64(loadTextContent('../app/server.py'))
            }
            {
              name: 'HTML_BASE64'
              value: base64(loadTextContent('../app/index.html'))
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Startup'
              httpGet: {
                path: '/health'
                port: 8080
              }
              initialDelaySeconds: 5
              periodSeconds: 5
              failureThreshold: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8080
              }
              periodSeconds: 10
              failureThreshold: 3
            }
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8080
              }
              periodSeconds: 20
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
        rules: [
          {
            name: 'http-ofertas'
            http: {
              metadata: { concurrentRequests: '2' }
            }
          }
        ]
      }
    }
  }
}
output appName string = app.name
output url string = 'https://${app.properties.configuration.ingress.fqdn}'

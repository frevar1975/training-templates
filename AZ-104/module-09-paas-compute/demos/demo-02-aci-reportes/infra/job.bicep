param location string
param suffix string
resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stacirep${suffix}'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
  }
}
resource files 'Microsoft.Storage/storageAccounts/fileServices@2023-05-01' = {
  parent: storage
  name: 'default'
}
resource share 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-05-01' = {
  parent: files
  name: 'reportes'
  properties: {
    shareQuota: 5
  }
}
resource group 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: 'aci-reportes-demo'
  location: location
  properties: {
    osType: 'Linux'
    restartPolicy: 'Never'
    containers: [
      {
        name: 'generador'
        properties: {
          image: 'python:3.12-slim-bookworm'
          command: [
            'python'
            '-u'
            '-c'
            'import base64,os;exec(compile(base64.b64decode(os.environ["REPORT_CODE_BASE64"]),"report.py","exec"))'
          ]
          environmentVariables: [
            {
              name: 'REPORT_CODE_BASE64'
              value: base64(loadTextContent('../app/report.py'))
            }
            {
              name: 'SEED_CSV_BASE64'
              value: base64(loadTextContent('../data/ventas.csv'))
            }
            {
              name: 'DEMO_DELAY_SECONDS'
              value: '60'
            }
          ]
          resources: {
            requests: {
              cpu: 1
              memoryInGB: 1.5
            }
          }
          volumeMounts: [
            {
              name: 'reportes'
              mountPath: '/reports'
              readOnly: false
            }
          ]
        }
      }
    ]
    volumes: [
      {
        name: 'reportes'
        azureFile: {
          shareName: share.name
          storageAccountName: storage.name
          storageAccountKey: storage.listKeys().keys[0].value
        }
      }
    ]
  }
  dependsOn: [
    share
  ]
}
output containerGroupName string = group.name
output storageAccountName string = storage.name

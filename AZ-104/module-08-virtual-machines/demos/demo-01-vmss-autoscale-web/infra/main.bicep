targetScope = 'subscription'

@minLength(1)
@maxLength(40)
param environmentName string
param location string
param sshPublicKey string
param vmSize string = 'Standard_D2s_v5'

resource demoGroup 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: {
    'azd-env-name': environmentName
    demo: 'AZ104 escalado web'
  }
}

module web 'web.bicep' = {
  name: 'web-${environmentName}'
  scope: demoGroup
  params: {
    location: location
    sshPublicKey: sshPublicKey
    vmSize: vmSize
    initialInstances: 1
    cpuThreshold: 60
    enableAutoscale: true
  }
}

output AZURE_RESOURCE_GROUP string = demoGroup.name
output DEMO_URL string = web.outputs.url
output VMSS_ID string = web.outputs.vmssId
output VMSS_NAME string = 'vmss-demo'
output AUTOSCALE_NAME string = 'auto-web'

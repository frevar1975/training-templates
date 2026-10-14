targetScope = 'subscription'
@minLength(1)
@maxLength(32)
param environmentName string
param location string
resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: {
    'azd-env-name': environmentName
    course: 'AZ104'
    demo: 'ACI reportes'
  }
}
module job 'job.bicep' = {
  name: 'report-${environmentName}'
  scope: rg
  params: {
    location: location
    suffix: uniqueString(subscription().id, rg.id)
  }
}
output AZURE_RESOURCE_GROUP string = rg.name
output CONTAINER_GROUP_NAME string = job.outputs.containerGroupName
output STORAGE_ACCOUNT_NAME string = job.outputs.storageAccountName
output FILE_SHARE_NAME string = 'reportes'
output CONTAINER_NAME string = 'generador'

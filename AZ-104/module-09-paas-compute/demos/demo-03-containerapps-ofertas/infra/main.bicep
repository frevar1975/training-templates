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
    demo: 'Container Apps ofertas'
  }
}
module web 'web.bicep' = {
  name: 'ofertas-${environmentName}'
  scope: rg
  params: {
    location: location
    suffix: uniqueString(subscription().id, rg.id)
  }
}
output AZURE_RESOURCE_GROUP string = rg.name
output CONTAINER_APP_NAME string = web.outputs.appName
output APPLICATION_URL string = web.outputs.url

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
    demo: 'App Service slots'
  }
}
module app 'web.bicep' = {
  name: 'slots-${environmentName}'
  scope: rg
  params: {
    location: location
    suffix: uniqueString(subscription().id, rg.id)
  }
}
output AZURE_RESOURCE_GROUP string = rg.name
output WEBAPP_NAME string = app.outputs.appName
output PRODUCTION_URL string = app.outputs.productionUrl
output STAGING_URL string = app.outputs.stagingUrl
output APP_SERVICE_PLAN_NAME string = app.outputs.planName

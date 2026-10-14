targetScope = 'resourceGroup'

@description('Región del grupo de recursos')
param location string = resourceGroup().location
@description('Clave SSH pública para las instancias Ubuntu')
param sshPublicKey string
param vmSize string = 'Standard_D2s_v5'
@minValue(1)
@maxValue(2)
param initialInstances int = 1
@minValue(1)
@maxValue(99)
param cpuThreshold int = 60
param enableAutoscale bool = true

// IDs de los componentes internos del balanceador y de la subred.
// resourceId evita referencias circulares dentro del mismo recurso.
var lbId = resourceId('Microsoft.Network/loadBalancers', 'lb-demo')
var vnetId = resourceId('Microsoft.Network/virtualNetworks', 'vnet-demo')
var frontendId = '${lbId}/frontendIPConfigurations/frontend'
var backendId = '${lbId}/backendAddressPools/backend'
var probeId = '${lbId}/probes/health'
var subnetId = '${vnetId}/subnets/web'

resource publicIp 'Microsoft.Network/publicIPAddresses@2023-09-01' = {
  name: 'pip-demo'
  location: location
  properties: {
    publicIPAllocationMethod: 'Static'
  }
  sku: {
    name: 'Standard'
  }
}

resource webNsg 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: 'nsg-demo'
  location: location
  properties: {
    securityRules: [
      {
        name: 'Web8080'
        properties: {
          priority: 100
          access: 'Allow'
          direction: 'Inbound'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '8080'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'HealthProbe8080'
        properties: {
          priority: 110
          access: 'Allow'
          direction: 'Inbound'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '8080'
          sourceAddressPrefix: 'AzureLoadBalancer'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

resource webVnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: 'vnet-demo'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.80.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'web'
        properties: {
          addressPrefix: '10.80.1.0/24'
          networkSecurityGroup: {
            id: webNsg.id
          }
          defaultOutboundAccess: false
        }
      }
    ]
  }
  dependsOn: [
    webNsg
  ]
}

resource webLb 'Microsoft.Network/loadBalancers@2023-09-01' = {
  name: 'lb-demo'
  location: location
  properties: {
    frontendIPConfigurations: [
      {
        name: 'frontend'
        properties: {
          publicIPAddress: {
            id: publicIp.id
          }
        }
      }
    ]
    backendAddressPools: [
      {
        name: 'backend'
      }
    ]
    probes: [
      {
        name: 'health'
        properties: {
          protocol: 'Http'
          port: 8080
          requestPath: '/health'
          intervalInSeconds: 5
          numberOfProbes: 2
        }
      }
    ]
    loadBalancingRules: [
      {
        name: 'web'
        properties: {
          frontendIPConfiguration: {
            id: frontendId
          }
          backendAddressPool: {
            id: backendId
          }
          probe: {
            id: probeId
          }
          protocol: 'Tcp'
          frontendPort: 80
          backendPort: 8080
          enableFloatingIP: false
          disableOutboundSnat: true
          idleTimeoutInMinutes: 4
          loadDistribution: 'Default'
        }
      }
    ]
    outboundRules: [
      {
        name: 'outbound'
        properties: {
          frontendIPConfigurations: [
            {
              id: frontendId
            }
          ]
          backendAddressPool: {
            id: backendId
          }
          protocol: 'All'
          allocatedOutboundPorts: 1024
          idleTimeoutInMinutes: 4
          enableTcpReset: true
        }
      }
    ]
  }
  sku: {
    name: 'Standard'
  }
  dependsOn: [
    publicIp
  ]
}

resource webVmss 'Microsoft.Compute/virtualMachineScaleSets@2023-09-01' = {
  name: 'vmss-demo'
  location: location
  properties: {
    orchestrationMode: 'Uniform'
    overprovision: false
    upgradePolicy: {
      mode: 'Manual'
    }
    virtualMachineProfile: {
      osProfile: {
        computerNamePrefix: 'az104web'
        adminUsername: 'azureuser'
        customData: base64(replace(loadTextContent('cloud-init.yaml'), '__APP_BASE64__', base64(loadTextContent('../app.py'))))
        linuxConfiguration: {
          disablePasswordAuthentication: true
          ssh: {
            publicKeys: [
              {
                path: '/home/azureuser/.ssh/authorized_keys'
                keyData: sshPublicKey
              }
            ]
          }
        }
      }
      storageProfile: {
        imageReference: {
          publisher: 'Canonical'
          offer: '0001-com-ubuntu-server-jammy'
          sku: '22_04-lts-gen2'
          version: 'latest'
        }
        osDisk: {
          createOption: 'FromImage'
          managedDisk: {
            storageAccountType: 'StandardSSD_LRS'
          }
        }
      }
      networkProfile: {
        networkInterfaceConfigurations: [
          {
            name: 'nic'
            properties: {
              primary: true
              ipConfigurations: [
                {
                  name: 'ipconfig'
                  properties: {
                    primary: true
                    subnet: {
                      id: subnetId
                    }
                    loadBalancerBackendAddressPools: [
                      {
                        id: backendId
                      }
                    ]
                  }
                }
              ]
            }
          }
        ]
      }
    }
  }
  sku: {
    name: vmSize
    tier: 'Standard'
    capacity: initialInstances
  }
  dependsOn: [
    webVnet
    webLb
  ]
}

// Autoscaling pertenece también a la plantilla Bicep.
resource webAutoscale 'Microsoft.Insights/autoscaleSettings@2022-10-01' = {
  name: 'auto-web'
  location: location
  properties: {
    enabled: enableAutoscale
    targetResourceUri: webVmss.id
    profiles: [
      {
        name: 'default'
        capacity: {
          minimum: '1'
          maximum: '2'
          default: string(initialInstances)
        }
        rules: [
          {
            metricTrigger: {
              metricName: 'Percentage CPU'
              metricNamespace: 'Microsoft.Compute/virtualMachineScaleSets'
              metricResourceUri: webVmss.id
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT5M'
              timeAggregation: 'Average'
              operator: 'GreaterThan'
              threshold: cpuThreshold
            }
            scaleAction: {
              direction: 'Increase'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT5M'
            }
          }
          {
            metricTrigger: {
              metricName: 'Percentage CPU'
              metricNamespace: 'Microsoft.Compute/virtualMachineScaleSets'
              metricResourceUri: webVmss.id
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT5M'
              timeAggregation: 'Average'
              operator: 'LessThan'
              threshold: 25
            }
            scaleAction: {
              direction: 'Decrease'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT5M'
            }
          }
        ]
      }
    ]
  }
}

output url string = 'http://${publicIp.properties.ipAddress}'
output vmssId string = webVmss.id
output autoscaleId string = webAutoscale.id

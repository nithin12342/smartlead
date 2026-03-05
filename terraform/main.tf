# SmartLead Terraform Configuration
# Spec-Driven: Generated from SmartLead/harness.json infrastructure_harness
# Azure Resource Manager Provider

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
  
  backend "azurerm" {
    resource_group_name  = "smartlead-tf-state"
    storage_account_name = "smartleadtfstate"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
  
  subscription_id = var.azure_subscription_id
  tenant_id       = var.azure_tenant_id
  client_id       = var.azure_client_id
  client_secret   = var.azure_client_secret
}

# Variables
variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
  sensitive   = true
}

variable "azure_tenant_id" {
  description = "Azure Tenant ID"
  type        = string
  sensitive   = true
}

variable "azure_client_id" {
  description = "Azure Client ID (Service Principal)"
  type        = string
  sensitive   = true
}

variable "azure_client_secret" {
  description = "Azure Client Secret"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

# Resource Group
resource "azurerm_resource_group" "smartlead" {
  name     = "smartlead-${var.environment}"
  location = var.location
  
  tags = {
    Environment = var.environment
    Project     = "SmartLead"
    ManagedBy   = "Terraform"
  }
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "smartlead" {
  name                = "smartlead-aks-${var.environment}"
  location            = azurerm_resource_group.smartlead.location
  resource_group_name = azurerm_resource_group.smartlead.name
  dns_prefix          = "smartlead"
  kubernetes_version  = "1.28"
  sku_tier            = var.environment == "prod" ? "Standard" : "Free"
  
  default_node_pool {
    name                = "default"
    node_count          = var.environment == "prod" ? 3 : 2
    vm_size             = "Standard_D4s_v3"
    type                = "VirtualMachineScaleSets"
    availability_zones  = ["1", "2", "3"]
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 6
    
    vnet_subnet_id = azurerm_subnet.aks.id
    
    node_labels = {
      "workload-type" = "general"
    }
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  azure_active_directory_role_based_access_control {
    managed = true
    azure_rbac_enabled = true
  }
  
  network_profile {
    network_plugin     = "azure"
    network_policy     = "calico"
    load_balancer_sku  = "standard"
    outbound_type      = "loadBalancer"
  }
  
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.smartlead.id
  }
  
  key_vault_secrets_provider {
    secret_rotation_enabled = true
  }
  
  tags = {
    Environment = var.environment
    Project     = "SmartLead"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "smartlead" {
  name                = "smartlead-vnet-${var.environment}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.smartlead.location
  resource_group_name = azurerm_resource_group.smartlead.name
}

# Subnet for AKS
resource "azurerm_subnet" "aks" {
  name                 = "aks-subnet"
  address_prefixes     = ["10.0.1.0/24"]
  virtual_network_name = azurerm_virtual_network.smartlead.name
  resource_group_name  = azurerm_resource_group.smartlead.name
}

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "smartlead" {
  name                   = "smartlead-pg-${var.environment}"
  location               = azurerm_resource_group.smartlead.location
  resource_group_name    = azurerm_resource_group.smartlead.name
  sku_name               = var.environment == "prod" ? "GeneralPurpose_D3s_v3" : "Burstable_B2ms"
  version                = "14"
  storage_mb             = 32768
  admin_username         = "smartlead"
  backup_retention_days  = 7
  
  high_availability {
    mode = var.environment == "prod" ? "ZoneRedundant" : "Disabled"
  }
  
  tags = {
    Environment = var.environment
    Project     = "SmartLead"
  }
}

# Redis Cache
resource "azurerm_redis_cache" "smartlead" {
  name                = "smartlead-redis-${var.environment}"
  location            = azurerm_resource_group.smartlead.location
  resource_group_name = azurerm_resource_group.smartlead.name
  sku_name            = var.environment == "prod" ? "Premium" : "Standard"
  capacity            = var.environment == "prod" ? 1 : 1
  family              = "P"
  
  redis_configuration {
    maxmemory_reserved    = 512
    maxmemory_delta       = 512
    maxmemory_policy      = "allkeys-lru"
    enable_authentication = true
  }
  
  tags = {
    Environment = var.environment
    Project     = "SmartLead"
  }
}

# Storage Account
resource "azurerm_storage_account" "smartlead" {
  name                     = "smartleadsa${var.environment}"
  resource_group_name      = azurerm_resource_group.smartlead.name
  location                 = azurerm_resource_group.smartlead.location
  account_tier             = "Standard"
  account_replication_type = var.environment == "prod" ? "GRS" : "LRS"
  enable_https_traffic_only = true
  
  blob_properties {
    versioning_enabled = true
    delete_retention_days = 90
  }
  
  tags = {
    Environment = var.environment
    Project     = "SmartLead"
  }
}

# Container Registry
resource "azurerm_container_registry" "smartlead" {
  name                   = "smartleadacr${var.environment}"
  resource_group_name    = azurerm_resource_group.smartlead.location
  location               = azurerm_resource_group.smartlead.name
  sku                    = "Standard"
  admin_enabled          = false
}

# Event Hubs
resource "azurerm_eventhub_namespace" "smartlead" {
  name                   = "smartlead-evh-${var.environment}"
  location               = azurerm_resource_group.smartlead.location
  resource_group_name    = azurerm_resource_group.smartlead.name
  sku                    = "Standard"
  capacity               = 1
}

resource "azurerm_eventhub" "smartlead" {
  name                = "smartlead-events"
  namespace_name      = azurerm_eventhub_namespace.smartlead.name
  resource_group_name = azurerm_resource_group.smartlead.name
  partition_count     = 4
  message_retention   = 7
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "smartlead" {
  name                = "smartlead-law-${var.environment}"
  location            = azurerm_resource_group.smartlead.location
  resource_group_name = azurerm_resource_group.smartlead.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Outputs
output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.smartlead.name
}

output "aks_cluster_id" {
  value = azurerm_kubernetes_cluster.smartlead.id
}

output "postgres_fqdn" {
  value = azurerm_postgresql_flexible_server.smartlead.fqdn
}

output "redis_hostname" {
  value = azurerm_redis_cache.smartlead.hostname
}

output "storage_account_name" {
  value = azurerm_storage_account.smartlead.name
}

output "container_registry_login_server" {
  value = azurerm_container_registry.smartlead.login_server
}

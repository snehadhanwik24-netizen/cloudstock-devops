resource "azurerm_virtual_network" "cloudstock_vnet" {
  name                = "cloudstock-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.cloudstock_rg.name
}
resource "azurerm_subnet" "cloudstock_subnet" {
  name                 = "cloudstock-subnet"
  resource_group_name  = azurerm_resource_group.cloudstock_rg.name
  virtual_network_name = azurerm_virtual_network.cloudstock_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}
resource "azurerm_public_ip" "cloudstock_public_ip" {
  name                = "cloudstock-public-ip"
  location            = var.location
  resource_group_name = azurerm_resource_group.cloudstock_rg.name
  allocation_method   = "Static"
}
resource "azurerm_network_security_group" "cloudstock_nsg" {
  name                = "cloudstock-nsg"
  location            = var.location
  resource_group_name = azurerm_resource_group.cloudstock_rg.name

  security_rule {
    name                       = "AllowSSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}
resource "azurerm_subnet_network_security_group_association" "cloudstock_nsg_assoc" {
  subnet_id                 = azurerm_subnet.cloudstock_subnet.id
  network_security_group_id = azurerm_network_security_group.cloudstock_nsg.id
}
provider "grafana" {
  url  = "http://54.89.122.83/"
  auth = "admin:admin"
}

resource "grafana_dashboard" "metrics" {
  config_json = "${file("3056.json")}"
}

resource "grafana_organization" "TsoftLatam" {
  name         = "Tsoft"
  admin_user   = "admin"
  create_users = true 
  viewers      = [
      "pcarrasco@a.com",
      "hites:hites"
  ]
}

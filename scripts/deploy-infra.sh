#!/bin/bash
# SmartLead Infrastructure Deployment Script
# Spec-Driven: Generated from SmartLead/harness.json automation_harness
# SOD (ShutDown/Operational/Deploy) Script

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${ENVIRONMENT:-development}"
TERRAFORM_DIR="$PROJECT_DIR/terraform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Usage function
usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

SmartLead Infrastructure Deployment Script

Commands:
    init        Initialize Terraform backend
    plan        Plan infrastructure changes
    apply       Apply infrastructure changes
    destroy     Destroy infrastructure
    validate    Validate Terraform configuration
    output      Show Terraform outputs

Options:
    -e, --environment   Environment (development/staging/production)
    -v, --verbose      Enable verbose output
    -h, --help         Show this help message

Examples:
    $0 init
    $0 plan -e production
    $0 apply -e staging
    $0 destroy -e development

EOF
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform not found. Please install Terraform >= 1.0"
        exit 1
    fi
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI not found. Please install Azure CLI"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_warn "kubectl not found. Some features may not work."
    fi
    
    log_info "Prerequisites check complete"
}

# Initialize Terraform
init_terraform() {
    log_info "Initializing Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    terraform init -upgrade
    
    log_info "Terraform initialized successfully"
}

# Plan infrastructure
plan_infrastructure() {
    log_info "Planning infrastructure for environment: $ENVIRONMENT"
    
    cd "$TERRAFORM_DIR"
    
    local tfvars_file="$ENVIRONMENT.tfvars"
    
    if [ -f "$tfvars_file" ]; then
        terraform plan -var-file="$tfvars_file" -out=tfplan
    else
        log_warn "No tfvars file found for $ENVIRONMENT, using defaults"
        terraform plan -out=tfplan
    fi
    
    log_info "Plan created successfully"
}

# Apply infrastructure
apply_infrastructure() {
    log_info "Applying infrastructure for environment: $ENVIRONMENT"
    
    cd "$TERRAFORM_DIR"
    
    if [ -f "tfplan" ]; then
        terraform apply tfplan
    else
        log_error "No plan file found. Run 'plan' first."
        exit 1
    fi
    
    log_info "Infrastructure applied successfully"
}

# Destroy infrastructure
destroy_infrastructure() {
    log_info "Destroying infrastructure for environment: $ENVIRONMENT"
    
    cd "$TERRAFORM_DIR"
    
    local tfvars_file="$ENVIRONMENT.tfvars"
    
    if [ -f "$tfvars_file" ]; then
        terraform destroy -var-file="$tfvars_file" -auto-approve
    else
        terraform destroy -auto-approve
    fi
    
    log_info "Infrastructure destroyed successfully"
}

# Validate Terraform
validate_terraform() {
    log_info "Validating Terraform configuration..."
    
    cd "$TERRAFORM_DIR"
    
    terraform validate
    terraform fmt -check
    
    log_info "Terraform validation complete"
}

# Show outputs
show_outputs() {
    log_info "Showing Terraform outputs..."
    
    cd "$TERRAFORM_DIR"
    
    terraform output
}

# Main execution
main() {
    local command="${1:-}"
    shift || true
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done
    
    # Check prerequisites
    check_prerequisites
    
    # Execute command
    case $command in
        init)
            init_terraform
            ;;
        plan)
            plan_infrastructure
            ;;
        apply)
            apply_infrastructure
            ;;
        destroy)
            destroy_infrastructure
            ;;
        validate)
            validate_terraform
            ;;
        output)
            show_outputs
            ;;
        *)
            usage
            ;;
    esac
}

main "$@"

class MasterDataGrpcClient:
    def __init__(self, target_address: str): self.target = target_address
    def verify_or_create_anagrafica(self, vat_number: str, fiscal_name: str, tenant_id: str):
        # Chiamata gRPC deterministica a Spring Boot solo per Clienti/Fornitori
        pass

class InvoiceProcessorApplicationService:
    def __init__(self, sdi_parser, ai_agent, grpc_master_data_client, repository):
        self.parser = sdi_parser
        self.ai_agent = ai_agent
        self.master_data_client = grpc_master_data_client
        self.repository = repository

    async def execute_workflow(self, xml_content: bytes, tenant_id: str):
        # 1. Parse XML
        # 2. Chiama Spring Boot via gRPC per verificare l'Anagrafica Clienti/Fornitori
        # 3. AI Mappings e persistenza
        pass

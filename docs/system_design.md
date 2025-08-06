# Green Duty System Design

## Implementation approach

After analyzing the requirements from the PRD, we'll implement the Green Duty system as a modular, scalable application with the following technical approach:

### Technology Stack
- **Backend Framework**: FastAPI (Python) for high-performance API endpoints
- **Database**: PostgreSQL with PostGIS extension for geospatial data handling
- **Image Processing**: OpenCV and Pillow for image preprocessing
- **ML Integration**: Ollama client for Gemma 3n model integration
- **Caching**: Redis for model prediction caching and rate limiting
- **Authentication**: JWT-based authentication system
- **Containerization**: Docker for consistent deployment
- **Orchestration**: Kubernetes for scaling and management
- **Storage**: Object storage (S3-compatible) for image files

### Key Technical Challenges and Solutions

1. **Gemma 3n Model Integration**
   - Solution: Create a dedicated microservice for model interactions, enabling isolation and scalability
   - Implement prediction caching to improve performance for common tree species
   - Use asynchronous processing queue for handling batch analysis requests

2. **Geographic Suitability Analysis**
   - Solution: Integrate with open-source climate and soil databases
   - Implement a rule-based engine for species-location matching
   - Cache geographic data by region for faster lookups

3. **Spatial Analysis for Tree Proximity**
   - Solution: Utilize PostGIS spatial queries for efficient nearby tree detection
   - Implement configurable proximity rules based on tree species characteristics

4. **Environmental Scoring Algorithm**
   - Solution: Create a configurable scoring matrix for different tree types
   - Implement a weighted scoring system that considers species, location, proximity, and growth potential
   - Build an extensible framework to accommodate future scoring criteria

5. **Image Processing Pipeline**
   - Solution: Implement preprocessing to standardize images before ML analysis
   - Extract metadata from images including EXIF data where available
   - Create a validation system to ensure image quality and angle diversity

## Data structures and interfaces

The system will be structured with the following core components and interfaces:

```mermaid
classDiagram
    class User {
        +user_id: UUID
        +username: String
        +email: String
        +password_hash: String
        +organization: String
        +created_at: DateTime
        +last_login: DateTime
        +authenticate(email: String, password: String): bool
        +create_upload(latitude: float, longitude: float, images: List[bytes]): Upload
    }

    class Upload {
        +upload_id: UUID
        +user_id: UUID
        +latitude: float
        +longitude: float
        +planting_date: DateTime
        +upload_timestamp: DateTime
        +additional_notes: String
        +status: UploadStatus
        +add_image(image_data: bytes, image_type: String): Image
        +submit_for_analysis(): Analysis
        +get_status(): UploadStatus
    }

    class Image {
        +image_id: UUID
        +upload_id: UUID
        +image_url: String
        +image_type: String
        +upload_timestamp: DateTime
        +preprocess(): bytes
        +extract_metadata(): Dict
        +validate(): bool
    }

    class Analysis {
        +analysis_id: UUID
        +upload_id: UUID
        +species_common_name: String
        +species_scientific_name: String
        +species_confidence: float
        +estimated_age: float
        +age_confidence: float
        +analysis_timestamp: DateTime
        +model_version: String
        +identify_species(images: List[Image]): Dict
        +estimate_age(images: List[Image]): Dict
        +request_certification(): Certification
    }

    class Certification {
        +certification_id: UUID
        +analysis_id: UUID
        +environmental_score: float
        +species_score: float
        +geographic_suitability_score: float
        +proximity_score: float
        +certification_status: CertificationStatus
        +certification_timestamp: DateTime
        +expiration_date: DateTime
        +calculate_scores(analysis: Analysis): Dict
        +generate_recommendations(): List[Recommendation]
        +issue_certificate(): String
    }

    class Recommendation {
        +recommendation_id: UUID
        +certification_id: UUID
        +recommendation_type: String
        +description: String
        +priority: int
        +created_at: DateTime
        +generate_alternatives(species: String, location: Location): List[String]
        +format_for_display(): Dict
    }

    class GeoSuitabilityRule {
        +rule_id: UUID
        +species_scientific_name: String
        +min_latitude: float
        +max_latitude: float
        +min_longitude: float
        +max_longitude: float
        +min_elevation: float
        +max_elevation: float
        +soil_types: List[String]
        +climate_zones: List[String]
        +precipitation_requirements: Dict
        +temperature_requirements: Dict
        +created_at: DateTime
        +updated_at: DateTime
        +is_location_suitable(species: String, latitude: float, longitude: float): bool
        +get_suitable_species(latitude: float, longitude: float): List[String]
    }

    class TreeSpecies {
        +species_id: UUID
        +common_name: String
        +scientific_name: String
        +type: SpeciesType
        +oxygen_production: float
        +carbon_sequestration: float
        +fruit_bearing: bool
        +native_regions: List[String]
        +get_environmental_score(): float
        +is_suitable_for_location(latitude: float, longitude: float): bool
    }

    class GemmaModelService {
        +model_name: String
        +model_version: String
        +initialize_model(): bool
        +predict_species(images: List[bytes]): Dict
        +predict_age(images: List[bytes], species: String): Dict
        +health_check(): bool
    }

    class ProximityChecker {
        +check_nearby_trees(latitude: float, longitude: float, radius: float): List[Dict]
        +calculate_optimal_spacing(species: String): float
        +validate_planting_location(latitude: float, longitude: float, species: String): bool
    }

    class ScoringEngine {
        +calculate_species_score(species: String): float
        +calculate_suitability_score(species: String, latitude: float, longitude: float): float
        +calculate_proximity_score(latitude: float, longitude: float, species: String): float
        +calculate_overall_score(species_score: float, suitability_score: float, proximity_score: float): float
    }

    class APIService {
        +handle_upload(request_data: Dict): Response
        +process_analysis(upload_id: UUID): Response
        +generate_certification(analysis_id: UUID): Response
        +get_upload_status(upload_id: UUID): Response
        +get_analysis_results(analysis_id: UUID): Response
        +get_certification(certification_id: UUID): Response
    }

    class AuthService {
        +issue_token(user: User): String
        +verify_token(token: String): bool
        +refresh_token(token: String): String
        +validate_permissions(user_id: UUID, resource: String, action: String): bool
    }

    User "1" --> "*" Upload: creates
    Upload "1" --> "*" Image: contains
    Upload "1" --> "1" Analysis: processed into
    Analysis "1" --> "1" Certification: evaluated as
    Certification "1" --> "*" Recommendation: generates
    Analysis --> GemmaModelService: uses
    Certification --> ScoringEngine: uses
    ScoringEngine --> TreeSpecies: references
    ScoringEngine --> GeoSuitabilityRule: applies
    ScoringEngine --> ProximityChecker: utilizes
    APIService --> AuthService: secures with
    APIService --> User: authenticates
    APIService --> Upload: manages
    APIService --> Analysis: initiates
    APIService --> Certification: issues
```

## Program call flow

The system interaction flow for the three main API endpoints:

```mermaid
sequenceDiagram
    participant Client
    participant APIGateway as API Gateway
    participant Auth as Auth Service
    participant Upload as Image Upload Service
    participant Storage as Object Storage
    participant Queue as Analysis Queue
    participant Gemma as Gemma Model Service
    participant Geo as Geo Suitability Service
    participant Proximity as Proximity Service
    participant Scoring as Scoring Engine
    participant DB as Database

    %% Authentication Flow
    Client->>APIGateway: Authentication Request
    APIGateway->>Auth: Validate Credentials
    Auth->>DB: Check User Credentials
    DB-->>Auth: User Validation Result
    Auth-->>APIGateway: JWT Token
    APIGateway-->>Client: Authentication Response

    %% Image Upload API Flow
    Client->>APIGateway: POST /api/v1/upload (with images & location)
    APIGateway->>Auth: Validate JWT Token
    Auth-->>APIGateway: Validation Result
    APIGateway->>Upload: Process Upload Request
    Upload->>DB: Create Upload Record
    DB-->>Upload: Upload ID
    par Process Each Image
        Upload->>Storage: Store Image 1
        Storage-->>Upload: Image 1 URL
        Upload->>DB: Store Image 1 Metadata
        Upload->>Storage: Store Image 2
        Storage-->>Upload: Image 2 URL
        Upload->>DB: Store Image 2 Metadata
        Upload->>Storage: Store Image 3
        Storage-->>Upload: Image 3 URL
        Upload->>DB: Store Image 3 Metadata
    end
    Upload-->>APIGateway: Upload Success Response
    APIGateway-->>Client: Upload Response with Upload ID

    %% Tree Analysis API Flow
    Client->>APIGateway: POST /api/v1/analyze (with upload_id)
    APIGateway->>Auth: Validate JWT Token
    Auth-->>APIGateway: Validation Result
    APIGateway->>Queue: Queue Analysis Job
    Queue->>DB: Update Upload Status (Processing)
    Queue->>Storage: Retrieve Image URLs
    Storage-->>Queue: Image URLs
    Queue->>Gemma: Request Species Identification
    Gemma->>Storage: Fetch Images
    Storage-->>Gemma: Image Data
    Gemma-->>Queue: Species Identification Results
    Queue->>Gemma: Request Age Estimation
    Gemma-->>Queue: Age Estimation Results
    Queue->>DB: Store Analysis Results
    DB-->>Queue: Analysis ID
    Queue-->>APIGateway: Analysis Complete Notification
    APIGateway-->>Client: Analysis Results Response

    %% Certification API Flow
    Client->>APIGateway: POST /api/v1/certify (with analysis_id)
    APIGateway->>Auth: Validate JWT Token
    Auth-->>APIGateway: Validation Result
    APIGateway->>Scoring: Request Certification
    Scoring->>DB: Retrieve Analysis Data
    DB-->>Scoring: Analysis Data
    Scoring->>DB: Retrieve Species Info
    DB-->>Scoring: Species Information
    Scoring->>Geo: Check Geographic Suitability
    Geo->>DB: Get Location Rules
    DB-->>Geo: Suitability Rules
    Geo-->>Scoring: Suitability Score
    Scoring->>Proximity: Check Nearby Trees
    Proximity->>DB: Spatial Query for Nearby Trees
    DB-->>Proximity: Nearby Tree Data
    Proximity-->>Scoring: Proximity Score
    Scoring->>Scoring: Calculate Environmental Score
    Scoring->>DB: Store Certification Results
    DB-->>Scoring: Certification ID
    Scoring->>Scoring: Generate Recommendations
    Scoring->>DB: Store Recommendations
    Scoring-->>APIGateway: Certification Complete
    APIGateway-->>Client: Certification Results Response
```

## System Architecture

### Component Diagram

```mermaid
graph TD
    Client[Client Applications] --> APIGateway[API Gateway/Load Balancer]
    APIGateway --> AuthService[Authentication Service]
    APIGateway --> UploadAPI[Image Upload API]
    APIGateway --> AnalysisAPI[Tree Analysis API]
    APIGateway --> CertificationAPI[Certification API]
    
    UploadAPI --> ImageProcessor[Image Processing Service]
    ImageProcessor --> ObjectStorage[(Object Storage)]
    
    AnalysisAPI --> AnalysisQueue[Analysis Job Queue]
    AnalysisQueue --> ModelService[Gemma 3n Model Service]
    ModelService --> ModelCache[(Redis Cache)]
    
    CertificationAPI --> ScoringEngine[Scoring Engine]
    ScoringEngine --> GeoService[Geographic Suitability Service]
    ScoringEngine --> ProximityService[Tree Proximity Service]
    
    AuthService --> Database[(PostgreSQL/PostGIS)]
    UploadAPI --> Database
    AnalysisAPI --> Database
    CertificationAPI --> Database
    GeoService --> Database
    ProximityService --> Database
    
    GeoService --> ExternalGeoData[External Geographic Data APIs]
```

## Deployment Strategy

The Green Duty system will be deployed using a containerized microservices architecture:

1. **Containerization**
   - Each service will be packaged as a Docker container
   - Standard base images will ensure consistency across environments
   - Container health checks and monitoring will be implemented

2. **Kubernetes Orchestration**
   - Service pods will auto-scale based on load
   - Resource limits to prevent single service overconsumption
   - Rolling updates for zero-downtime deployments
   - Readiness and liveness probes for service health

3. **Multi-Environment Setup**
   - Development environment for feature development
   - Testing environment for QA and integration testing
   - Staging environment mimicking production
   - Production environment with enhanced security and monitoring

4. **Database Deployment**
   - PostgreSQL with PostGIS as a managed service or in-cluster stateful set
   - Regular automated backups
   - Read replicas for scaling query performance

5. **Model Deployment**
   - Dedicated high-performance nodes for running Gemma 3n model
   - GPU acceleration where available
   - Model versioning and A/B testing capabilities

6. **Infrastructure as Code**
   - Terraform for provisioning cloud resources
   - Helm charts for Kubernetes deployments
   - Configuration management via Kubernetes ConfigMaps and Secrets

## Security Considerations

1. **API Security**
   - JWT-based authentication for all API endpoints
   - Role-based access control (RBAC) for different user types
   - API rate limiting to prevent abuse
   - Input validation and sanitization
   - HTTPS/TLS for all communications

2. **Data Security**
   - Encryption at rest for all data storage
   - Data anonymization for reporting purposes
   - Proper handling of personally identifiable information (PII)
   - Secure deletion policies for removed data

3. **Model Security**
   - Isolation of model service from public networks
   - Input validation to prevent adversarial attacks
   - Monitoring for unusual prediction patterns

4. **Infrastructure Security**
   - Network segmentation and firewall rules
   - Kubernetes pod security policies
   - Regular security scans and patching
   - Principle of least privilege for service accounts

5. **Compliance and Auditing**
   - Comprehensive logging for all system operations
   - Audit trail for certification issuance
   - Regular security audits and penetration testing
   - Compliance with relevant data protection regulations

## Monitoring and Observability

1. **Service Monitoring**
   - Prometheus for metrics collection
   - Grafana dashboards for visualization
   - Alerting for critical service degradation

2. **Model Monitoring**
   - Track prediction accuracy and confidence scores
   - Monitor prediction latency and resource usage
   - Alert on drift or degradation in model performance

3. **User Experience Monitoring**
   - Track API response times
   - Monitor upload and processing success rates
   - Gather user feedback on recommendations

## Scalability Considerations

1. **Horizontal Scaling**
   - Stateless services designed for horizontal scaling
   - Database read replicas and connection pooling
   - Distributed caching for high-traffic data

2. **Batch Processing**
   - Asynchronous processing of image analysis tasks
   - Job queues with prioritization and fair scheduling
   - Parallelized processing where possible

3. **Geographic Distribution**
   - Edge caching for static resources
   - CDN integration for image delivery
   - Regional API endpoints for reduced latency

## Anything UNCLEAR

1. **Oxygen Absorption Criteria**: The PRD mentions "trees that absorb oxygen from the environment will receive negative points," which is scientifically unusual as trees generally produce oxygen and absorb carbon dioxide. This requirement needs clarification - perhaps it refers to certain plant species or specific environmental conditions.

2. **Scale of Deployment**: The expected request volume and user base size are not specified, which affects architectural decisions around scaling and performance optimization.

3. **Offline Capabilities**: Whether the system should support offline operation for field work in areas with limited connectivity is not clearly specified.

4. **Model Update Strategy**: How frequently the Gemma 3n model will be updated and how to handle backward compatibility for existing analyses needs clarification.

5. **Tree Proximity Definition**: The specific minimum distance required between trees needs to be defined, potentially as a species-specific parameter.

6. **Legal and Compliance Requirements**: Any specific legal requirements for tree certification or data handling should be clarified.
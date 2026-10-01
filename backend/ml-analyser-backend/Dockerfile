FROM eclipse-temurin:25-jdk

WORKDIR /app

COPY . .

RUN sed -i 's/\r$//' mvnw
RUN chmod +x mvnw
RUN ./mvnw clean package -DskipTests

CMD ["java", "-jar", "target/ml-analyser-backend-0.0.1-SNAPSHOT.jar"]

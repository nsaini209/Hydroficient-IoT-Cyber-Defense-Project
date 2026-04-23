import ipaddress
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


#This is going to Generate the Certificate Authority (CA) certificate (Self-signed)
def generate_ca_certificate():

    # Generate a private key for the CA using RSA with a key size of 2048 bits
    # public_exponent=65537 is a standard, secure value for RSA keys
    # 2048 bits is a common encryption for secure learning, bigger production environments may use 4096 bits

    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # x509 is the main certificate class in the cryptography library.
    # This is defining the certificates identity

    ca_name = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Grand Marina Hotel"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Water Systems Security"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Grand Marina Root CA"),
    ])

    # Building and signing the CA certificate.

    ca_cert  = (
        x509.CertificateBuilder()
        .subject_name(ca_name)  # The entity this certificate represents
        .issuer_name(ca_name)   # The entity that signed the certificate (self-signed here)
        .public_key(ca_key.public_key())  # The public key associated with this certificate
        .serial_number(x509.random_serial_number())  # Unique identifier for the certificate
        .not_valid_before(datetime.now(timezone.utc))  # Valid from yesterday (to avoid clock skew issues)
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))  # Valid for 10 years
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True,
        )  # Marks this as a CA certificate
        .sign(ca_key, hashes.SHA256())  # Sign the certificate with the CA's private key
    )
    return ca_key, ca_cert

    # Creating the Server Certificate for the MQTT broker, signed by the CA. 
    # This tells the Sensor, I am verified by the CA, you can trust me.

def generate_server_certificate(ca_key, ca_cert):
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048) # This is teh same as the CA key generation, but for the server. Giving it the private key.

    # This is the servers identity
    server_name = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Grand Marina Hotel"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "MQTT Broker"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"), # Common name must match hostname clients to connect. (In this case we use local host for testing)
    ])

    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_name)  # The entity this certificate represents
        .issuer_name(ca_cert.subject)  # The CA that signed this certificate
        .public_key(server_key.public_key())  # The public key associated with this certificate
        .serial_number(x509.random_serial_number())  # Unique identifier for the certificate
        .not_valid_before(datetime.now(timezone.utc))  # Valid from yesterday (to avoid clock skew issues)
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))  
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
            critical=False,
        )  # Allows clients to verify the server's identity using the hostname
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None), 
            critical=True,
        )  # Indicates this certificate is for server authentication
        .sign(ca_key, hashes.SHA256())  # Sign the certificate with the CA's private key1
    )
    return server_key, server_cert


# Saving the Certificate and the broker's certificate.
def save_certificates(ca_cert, server_cert, server_key, output_dir="certs"):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Save CA certificate and key
    with open(output_path / "ca.pem", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

        # Save the server certificate (public)
    with open(output_path / "server.pem", "wb") as f:
        f.write(server_cert.public_bytes(encoding=serialization.Encoding.PEM))

    # Save Server certificate and key (SECRET!)

    with open(output_path / "server-key.pem", "wb") as f:
        f.write(server_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

if __name__ == "__main__":
    print("=" * 55)
    print("  Certificate Generation for Grand Marina Hotel")
    print("=" * 55)

    print("\n[1/3] Generating Certificate Authority (CA)...")
    print("      Generating CA private key (2048 bits)...")
    print("      Creating CA certificate (valid for 10 years)...")
    ca_key, ca_cert = generate_ca_certificate()
    print("      CA certificate created successfully!")

    print("\n[2/3] Generating Server Certificate...")
    print("      Generating server private key (2048 bits)...")
    print("      Creating server certificate (valid for 1 year)...")
    print("      Common Name: localhost")
    print("      Subject Alternative Names: localhost, 127.0.0.1")
    server_key, server_cert = generate_server_certificate(ca_key, ca_cert)
    print("      Server certificate created successfully!")

    print("\n[3/3] Saving certificates to certs/ folder...")
    save_certificates(ca_cert, server_cert, server_key)
    print("      Saved: certs\\ca.pem")
    print("      Saved: certs\\server.pem")
    print("      Saved: certs\\server-key.pem")

    print("      Verifying certificates...")
    print(f"      CA Subject: {ca_cert.subject.rfc4514_string()}")
    print(f"      CA Valid Until: {ca_cert.not_valid_after_utc.strftime('%Y-%m-%d')}")
    print(f"      Server Subject: {server_cert.subject.rfc4514_string()}")
    print(f"      Server Issuer: {server_cert.issuer.rfc4514_string()}")
    print(f"      Server Valid Until: {server_cert.not_valid_after_utc.strftime('%Y-%m-%d')}")
    print("      Chain verified: Server cert is signed by CA")

    print("\n" + "=" * 55)
    print("  Certificates generated successfully!")
    print("=" * 55)
    print("\nFiles created:")
    print("  certs/ca.pem         - CA certificate (share with clients)")
    print("  certs/server.pem     - Server certificate (for Mosquitto)")
    print("  certs/server-key.pem - Server private key (keep secret!)")
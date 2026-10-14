// Validate students.xml against students.xsd using plain Java (no extra library)
// Compile: javac Validate.java     Run: java Validate
import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.*;
import java.io.File;

public class Validate {
    public static void main(String[] args) {
        try {
            SchemaFactory factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
            Schema schema = factory.newSchema(new File("students.xsd"));
            Validator validator = schema.newValidator();
            validator.validate(new StreamSource(new File("students.xml")));
            System.out.println("XML is VALID according to the XSD");
        } catch (Exception e) {
            System.out.println("XML is INVALID: " + e.getMessage());
        }
    }
}


import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.parser.nndep.DependencyParser;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import edu.stanford.nlp.trees.*;

import java.io.StringReader;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.List;
import java.util.Properties;

/**
 * Parse review sentences with hash id in the first field
 * First use the tagger, then use the NN dependency
 * parser. Note that the parser will not work on untagged text.
 *
 * Adapted from DependencyParserDemo.java from Stanford parser
 */

public class ReviewDependencyParser {
  public static void main(String[] args) throws Exception {
    String modelPath = DependencyParser.DEFAULT_MODEL;
    String taggerPath = "edu/stanford/nlp/models/pos-tagger/english-left3words/english-left3words-distsim.tagger";

    String inputFilePath = "input.txt";
    String outputFilePath = "output.txt";
    String configFilePath = "ReviewDependencyParser.properties";

    // you may specify your tagger and model from command line
    for (int argIndex = 0; argIndex < args.length; ) {
      switch (args[argIndex]) {
        case "-tagger":
          taggerPath = args[argIndex + 1];
          argIndex += 2;
          break;
        case "-model":
          modelPath = args[argIndex + 1];
          argIndex += 2;
          break;
        case "-config":
          configFilePath = args[argIndex + 1];
          argIndex += 2;
          break;
        default:
          throw new RuntimeException("Unknown argument " + args[argIndex]);
      }
    }
    
    // prepare the tagger and parser
    MaxentTagger tagger = new MaxentTagger(taggerPath);
    DependencyParser parser = DependencyParser.loadFromModelFile(modelPath);
    
    Properties prop = new Properties();

    FileInputStream inputStream = new FileInputStream(configFilePath);

    prop.load(inputStream);

    Integer num_files = new Integer(prop.getProperty("num_files"));
    
    String data_path = prop.getProperty("data_path");

    for (int i = 0; i < num_files.intValue(); ++i) {
        // System.out.println(i);
        ProcessOneFile(tagger, parser, data_path + prop.getProperty("input." + i), data_path + prop.getProperty("output." + i));
    }
  }
  
  public static void ProcessOneFile(MaxentTagger tagger, DependencyParser parser, String inputFilePath, String outputFilePath) throws Exception {

      System.out.println("processing file: " + inputFilePath);

      // start reading input file
      BufferedReader br = new BufferedReader(new FileReader(new File(inputFilePath)));

      BufferedWriter writer = new BufferedWriter(new FileWriter(new File(outputFilePath)));

      String line;

      int line_num = 0;

      while ((line = br.readLine()) != null) {
          line_num++;
          if (line_num % 50 == 0) {
              System.out.println(line_num + " lines processed");
          }
          // System.out.println(line);
          String text = line.trim();

          String hash_id = text.substring(0,text.indexOf(' ')); // first field is the hash code of the review
          
          int field_length = hash_id.length();
          text = text.substring(field_length + 1);   // cut out the first field

          String feature_list = text.substring(0, text.indexOf(']')+1);
          field_length = feature_list.length();
          text = text.substring(field_length + 1);

          String opinion_list = text.substring(0, text.indexOf(']')+1);
          field_length = opinion_list.length();
          
          String review = text.substring(field_length + 1);// the remaining part is the review text
            
          //System.out.println(hash_id);
          //System.out.println(feature_list);
          //System.out.println(opinion_list);
          //System.out.println(review);
         
          DocumentPreprocessor tokenizer = new DocumentPreprocessor(new StringReader(review));

          String parsed_results = "[";

          for (List<HasWord> sentence : tokenizer) {
              List<TaggedWord> tagged = tagger.tagSentence(sentence);
              GrammaticalStructure gs = parser.predict(tagged);

              // Find typed dependencies
              List<TypedDependency> tdl = gs.typedDependenciesCCprocessed();

              for (TypedDependency td : tdl) {
                  // System.out.println(td.toString());
                  // output format: nsubj(purchased/VBD, i/LS),
                  parsed_results += td.reln().toString() + "(" + td.gov().toString() + ", " + td.dep().toString() + ")";
                  parsed_results += ",";
              }
          }

          // get rid of the last colon and add boundary symbols back
          writer.write(hash_id + " " + parsed_results.substring(0, parsed_results.length() - 1) + "]\n");
      }
      writer.close();
      br.close();
  }
}

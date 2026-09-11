package com.intentsim;

import java.io.*;
import java.net.*;
import java.util.*;

public class App {

    public static void main(String[] args) {

        try {

            // First test case - both programs perform addition
            String code1_case1 = """
                    class A {
                        void addNumbers() {
                            int a = 5;
                            int b = 3;
                            int result = a + b;
                            System.out.println(result);
                        }
                    }
                    """;

            String code2_case1 = """
                    class B {
                        void sumNumbers() {
                            int x = 5;
                            int y = 3;
                            int total = x + y;
                            System.out.println(total);
                        }
                    }
                    """;

            // Second test case - addition vs multiplication
            String code1_case2 = """
                    class A {
                        void addNumbers() {
                            int a = 5;
                            int b = 3;
                            int result = a + b;
                            System.out.println(result);
                        }
                    }
                    """;

            String code2_case2 = """
                    class B {
                        void multiplyNumbers() {
                            int x = 5;
                            int y = 3;
                            int result = x * y;
                            System.out.println(result);
                        }
                    }
                    """;

            // Third test case - completely different logic
            String code1_case3 = """
                    class A {
                        void addNumbers() {
                            int a = 5;
                            int b = 3;
                            int result = a + b;
                            System.out.println(result);
                        }
                    }
                    """;

            String code2_case3 = """
                    class B {
                        void factorial() {
                            int n = 5;
                            int fact = 1;
                            for (int i = 1; i <= n; i++) {
                                fact *= i;
                            }
                            System.out.println(fact);
                        }
                    }
                    """;

            runTest("CASE 1: SAME LOGIC", code1_case1, code2_case1);
            runTest("CASE 2: DIFFERENT LOGIC", code1_case2, code2_case2);
            runTest("CASE 3: COMPLETELY DIFFERENT", code1_case3, code2_case3);

        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    // Compare two methods and print the similarity score
    public static void runTest(String title, String code1, String code2) throws Exception {

        System.out.println("\n==============================");
        System.out.println(title);
        System.out.println("==============================");

        List<String> methods1 = MethodExtractor.extractMethods(code1);
        List<String> methods2 = MethodExtractor.extractMethods(code2);

        String method1 = methods1.get(0);
        String method2 = methods2.get(0);

        double similarity = getSimilarity(method1, method2);

        System.out.println("Similarity: " + similarity + "%");
    }

    // Send both methods to the Python server
    public static double getSimilarity(String code1, String code2) throws Exception {

        URL url = new URL("http://127.0.0.1:5000/similarity");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);

        // Remove new lines before sending JSON
        String cleanCode1 = code1.replace("\n", " ")
                                 .replace("\r", " ")
                                 .replace("\"", "\\\"");

        String cleanCode2 = code2.replace("\n", " ")
                                 .replace("\r", " ")
                                 .replace("\"", "\\\"");

        String jsonInput = String.format(
                "{\"code1\":\"%s\",\"code2\":\"%s\"}",
                cleanCode1,
                cleanCode2
        );

        OutputStream os = conn.getOutputStream();
        os.write(jsonInput.getBytes());
        os.flush();

        InputStream is;

        if (conn.getResponseCode() >= 200 && conn.getResponseCode() < 300) {
            is = conn.getInputStream();
        } else {
            is = conn.getErrorStream();
        }

        BufferedReader br = new BufferedReader(new InputStreamReader(is));

        String response = br.readLine();
        String number = response.replaceAll("[^0-9.]", "");

        return Double.parseDouble(number);
    }
}
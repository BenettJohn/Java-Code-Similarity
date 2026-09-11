package com.intentsim;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;

import java.util.ArrayList;
import java.util.List;

public class MethodExtractor {

    public static List<String> extractMethods(String code) {

        List<String> methods = new ArrayList<>();

        // Parse the Java source code
        CompilationUnit cu = StaticJavaParser.parse(code);

        // Collect all methods from the program
        for (MethodDeclaration method : cu.findAll(MethodDeclaration.class)) {
            methods.add(method.toString());
        }

        return methods;
    }
}
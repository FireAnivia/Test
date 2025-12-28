import java.util.Scanner;

/**
 * IO class for OPLang runtime.
 * Provides input/output operations for OPLang programs.
 */
public class io {
    private static Scanner scanner = new Scanner(System.in);
    
    // Integer I/O
    public static int readInt() {
        return scanner.nextInt();
    }
    
    public static void writeInt(int anArg) {
        System.out.print(anArg);
    }
    
    public static void writeIntLn(int anArg) {
        System.out.println(anArg);
    }
    
    // Float I/O
    public static float readFloat() {
        return scanner.nextFloat();
    }
    
    public static void writeFloat(float anArg) {
        System.out.print(anArg);
    }
    
    public static void writeFloatLn(float anArg) {
        System.out.println(anArg);
    }
    
    // Boolean I/O
    public static boolean readBool() {
        String input = scanner.next().toLowerCase();
        return input.equals("true") || input.equals("1");
    }
    
    public static void writeBool(boolean anArg) {
        System.out.print(anArg);
    }
    
    public static void writeBoolLn(boolean anArg) {
        System.out.println(anArg);
    }
    
    // String I/O
    public static String readStr() {
        return scanner.next();
    }
    
    public static void writeStr(String anArg) {
        System.out.print(anArg);
    }
    
    public static void writeStrLn(String anArg) {
        System.out.println(anArg);
    }
}


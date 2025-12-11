namespace UVM_Assembler.Interpreter;

public static class ALU
{
    public static int Divide(int a, int b)
    {
        if (b == 0)
            throw new DivideByZeroException("Division by zero");
        
        return a / b;
    }
}
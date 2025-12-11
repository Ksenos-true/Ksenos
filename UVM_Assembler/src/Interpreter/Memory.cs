namespace UVM_Assembler.Interpreter;

public class Memory
{
    private const int MEMORY_SIZE = 65536;
    private int[] memory;
    
    public Memory()
    {
        memory = new int[MEMORY_SIZE];
    }
    
    public int Read(int address)
    {
        if (address < 0 || address >= MEMORY_SIZE)
            throw new IndexOutOfRangeException($"Memory address {address} out of range");
        
        return memory[address];
    }
    
    public void Write(int address, int value)
    {
        if (address < 0 || address >= MEMORY_SIZE)
            throw new IndexOutOfRangeException($"Memory address {address} out of range");
        
        memory[address] = value;
    }
    
    public string DumpToXml(int startAddress, int endAddress)
    {
        if (startAddress < 0 || startAddress >= MEMORY_SIZE ||
            endAddress < 0 || endAddress >= MEMORY_SIZE ||
            startAddress > endAddress)
        {
            throw new ArgumentException($"Invalid address range: {startAddress}-{endAddress}");
        }
        
        var xml = new System.Text.StringBuilder();
        xml.AppendLine("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        xml.AppendLine("<memory_dump>");
        
        for (int i = startAddress; i <= endAddress; i++)
        {
            xml.AppendLine($"  <cell address=\"0x{i:X4}\" value=\"{memory[i]}\" />");
        }
        
        xml.AppendLine("</memory_dump>");
        return xml.ToString();
    }
    
    public void LoadData(int[] data, int startAddress = 0)
    {
        Array.Copy(data, 0, memory, startAddress, Math.Min(data.Length, MEMORY_SIZE - startAddress));
    }
}
import java.util.ArrayList;

/**
* MMU using least recently used replacement strategy
*/

public class LruMMU implements MMU {
    //instance variables 
    private int totalReads = 0;
    private int totalWrites = 0;
    private int pageFaults = 0;
    private ArrayList<Integer> pageTable;
    private ArrayList<Integer> dirty;
    private int lru_frames = 0;
    private int debugCheck = 0;

    public LruMMU(int frames) {
        this.lru_frames = frames;
        this.pageTable = new ArrayList<>();
        this.dirty = new ArrayList<>();
    }
    
    public void setDebug() {
        this.debugCheck = 1;
    }
    
    public void resetDebug() {
        this.debugCheck = 0;
    }
    
    public void readMemory(int page_number) {
        int checkDirty = 0;
        
        // instance of no page fault
        if(pageTable.contains(page_number)){
            pageTable.remove(Integer.valueOf(page_number));
            pageTable.add(0,page_number);

            //print statements in case of debug
            if(this.debugCheck == 1){
                System.out.println("Reading page:" + page_number);
                System.out.println("Page " + page_number + " found in memory. No page fault.");
                System.out.println();
            }

        //page fault but our page table is not full
        }else if(pageTable.size()<this.lru_frames){
            pageTable.add(0,page_number);
            this.totalReads = this.totalReads + 1;
            this.pageFaults = this.pageFaults + 1;

            if(this.debugCheck == 1){
                System.out.println("Reading page:" + page_number);
                System.out.println("Page " + page_number + " not in memory. Page fault.");
                System.out.println("Page table not full. Reading page " + page_number + " from disk.");
                System.out.println();
            }

        //page fault and our page table is full
        }else{
            checkDirty = pageTable.get(pageTable.size()-1);

            if(this.debugCheck == 1){
                System.out.println("Reading page:" + page_number);
                System.out.println("Page " + page_number + " not in memory.");
                System.out.println("Page table full. Replacing page " + checkDirty);

            }

            //write to memory if page to be removed is dirty
            if(dirty.contains(checkDirty)){
                if(this.debugCheck == 1){System.out.println("Page "+ checkDirty + " is dirty. Writing to disk.");}
                this.totalWrites = this.totalWrites + 1;
                dirty.remove(Integer.valueOf(checkDirty));
            }

            if(this.debugCheck == 1){System.out.println("Reading page " + page_number + " from disk."); System.out.println();}

            //read from memory to page table
            pageTable.remove(Integer.valueOf(checkDirty));
            pageTable.add(0,page_number);
            this.totalReads = this.totalReads + 1;
            this.pageFaults = this.pageFaults + 1;


        }
    }
    
    public void writeMemory(int page_number) {
        int checkDirty = 0;
        
        // instance of no page fault
        if(pageTable.contains(page_number)){
            pageTable.remove(Integer.valueOf(page_number));
            pageTable.add(0,page_number);

            //mark written page as dirty
            if(!dirty.contains(page_number)){
                dirty.add(0,page_number);
            }

            if(this.debugCheck == 1){
                System.out.println("Writing page:" + page_number);
                System.out.println("Page " + page_number + " found in memory. No page fault.");
                System.out.println("Marking page " + page_number + " as dirty.");
                System.out.println();
            }
        
        //page fault but our page table is not full
        }else if(pageTable.size()<this.lru_frames){
            pageTable.add(0,page_number);
            this.totalReads = this.totalReads + 1;
            this.pageFaults = this.pageFaults + 1;
            dirty.add(0,page_number);

            if(this.debugCheck == 1){
                System.out.println("Writing page:" + page_number);
                System.out.println("Page " + page_number + " not in memory. Page fault.");
                System.out.println("Page table not full. Reading page " + page_number + " from disk.");
                System.out.println("Marking page " + page_number + " as dirty.");
                System.out.println();
            }

        //page fault and our page table is full
        }else{
            checkDirty = pageTable.get(pageTable.size()-1);
            
            
            if(this.debugCheck == 1){
                System.out.println("Writing page:" + page_number);
                System.out.println("Page " + page_number + " not in memory.");
                System.out.println("Page table full. Replacing page " + checkDirty);

            }

            //write to memory if page to be removed is dirty
            if(dirty.contains(checkDirty)){
                if(this.debugCheck == 1){System.out.println("Page "+ checkDirty + " is dirty. Writing to disk.");}
                this.totalWrites = this.totalWrites + 1;
                dirty.remove(Integer.valueOf(checkDirty));
            }

            if(this.debugCheck == 1){
                System.out.println("Reading page " + page_number + " from disk."); 
                System.out.println("Marking page " + page_number + " as dirty.");
                System.out.println();
            }

            //read from memory to page table
            pageTable.remove(Integer.valueOf(checkDirty));
            pageTable.add(0,page_number);
            dirty.add(0,page_number);
            this.totalReads = this.totalReads + 1;
            this.pageFaults = this.pageFaults + 1;
        }
    }
    
    public int getTotalDiskReads() {
        return this.totalReads;
    }
    
    public int getTotalDiskWrites() {
        return this.totalWrites;
    }
    
    public int getTotalPageFaults() {
        return this.pageFaults;
    }
}
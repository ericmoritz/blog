Find the number of days until next day of week
##############################################
:date: 2008-07-10 23:03:29
:tags: date, python

I've had to figure this out before and I forgot it.  Here it is preserved

.. sourcecode::
   python


    def daysuntilnextdow(start, next):
        """Determine how many days until the next Day of week                                                                 
                                                                                                                              
        start: The day of the week to start from                                                                              
        next: The day of the week to go to                                                                                    
                                                                                                                              
        returns a number of days until the next day of week                                                                   
                                                                                                                              
        Note, start is inclusive, so if next is the same day,                                                                 
        you will receive 0                                                                                                    
                                                                                                                              
        Example:                                                                                                              
                                                                                                                              
        >> start = 0 # Sunday                                                                                                 
        >> next = 1 # Monday                                                                                                  
        >> daysuntilnextdow(start, next)                                                                                      
        1                                                                                                                     
        >> start = 3 # Wednesday                                                                                              
        >> next = 0 # Sunday                                                                                                
        >> daysuntilnextdow(start, next)                                                                                      
        4                                                                                                                     
        >> start = 0 # Sunday                                                                                                 
        >> next = 0 # Sunday                                                                                                  
        >> daysuntilnextdow(start, next)                                                                                      
        0                                                                                                                     
        """
        return ((next - start) % 7)

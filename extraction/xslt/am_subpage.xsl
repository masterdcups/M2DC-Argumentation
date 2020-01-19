<?xml version="1.0" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Output to text (csv) -->
  <xsl:output method="text"/>

  <!-- Root -->
  <xsl:template match="/">
    <xsl:apply-templates select="//h3" />
    <xsl:apply-templates select="/ul/li/div[2]" />
  </xsl:template>


  <!-- Name -->
  <xsl:template match="h3">
    <xsl:text>#name: </xsl:text>
    <xsl:value-of select="." />
    <xsl:text>&#xa;</xsl:text>
  </xsl:template>

  <!-- Arguments -->
  <xsl:template match="div">

    <!-- because / but / however -->
    <xsl:variable name="dtype">
      <xsl:value-of select="./@data-type" />
    </xsl:variable>

    <!-- Write CSV -->
    <xsl:text>--place-url-here--?partial=</xsl:text>
    <xsl:value-of select="./@data-id" />
    <xsl:text>&amp;level=0;</xsl:text>
    <xsl:value-of select="./div[3]" />
    <xsl:text>;</xsl:text>
    <xsl:choose>
      <xsl:when test="$dtype = 'because'">
	<xsl:text>1</xsl:text>
      </xsl:when>
      <xsl:when test="$dtype = 'but'">
	<xsl:text>-1</xsl:text>
      </xsl:when>
      <xsl:when test="$dtype = 'however'">
	<xsl:text>-0.5</xsl:text>
      </xsl:when>
      <xsl:otherwise>
	<xsl:text>0</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text>&#xa;</xsl:text> <!-- newline -->
  </xsl:template>

</xsl:stylesheet>
